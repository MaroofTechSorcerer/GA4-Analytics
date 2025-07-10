import streamlit as st
import json
import tempfile
import os
import pandas as pd
from nlq import nlq_to_ga4_params
from ga4_api import run_ga4_query
from datetime import datetime, timedelta
import io
import zipfile

# Ensure session state keys are initialized
if 'creds_path' not in st.session_state:
    st.session_state['creds_path'] = None
if 'property_id' not in st.session_state:
    st.session_state['property_id'] = ''
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''

st.set_page_config(page_title="GA4 Dashboard", layout="wide")
st.title("GA4 Analytics Dashboard (Custom UI)")

# --- Sidebar: OpenAI Key, Credentials, Property, Days Filter ---
st.sidebar.header("Setup")
if 'change_key' not in st.session_state:
    st.session_state['change_key'] = False
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''

if st.session_state['openai_api_key'] and not st.session_state['change_key']:
    st.sidebar.success("OpenAI API key loaded.")
    if st.sidebar.button("Change OpenAI API Key"):
        st.session_state['change_key'] = True
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state['openai_api_key'])
    if openai_api_key:
        st.session_state['openai_api_key'] = openai_api_key
        st.session_state['change_key'] = False

creds_file = st.sidebar.file_uploader("Upload GA4 credentials (.json)", type=["json"])
if creds_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(creds_file.read())
        st.session_state['creds_path'] = tmp.name
    st.sidebar.success("Credentials uploaded!")

property_id = st.sidebar.text_input("GA4 Property ID", value=st.session_state['property_id'])
if property_id:
    st.session_state['property_id'] = property_id

# Days filter
if 'days_filter' not in st.session_state:
    st.session_state['days_filter'] = 7
selected_days = st.sidebar.selectbox("Show data for the last...", [7, 14, 30, 90], index=[7, 14, 30, 90].index(st.session_state['days_filter']))
st.session_state['days_filter'] = selected_days
DEFAULT_START = (datetime.today() - timedelta(days=selected_days)).strftime('%Y-%m-%d')
DEFAULT_END = datetime.today().strftime('%Y-%m-%d')

# --- Helper for running queries ---
def safe_run_query(metrics, dimensions, start=None, end=None, limit=None):
    # Always use default date range if not provided
    if not start:
        start = DEFAULT_START
    if not end:
        end = DEFAULT_END
    try:
        df = run_ga4_query(
            st.session_state['property_id'],
            st.session_state['creds_path'],
            metrics, dimensions, start, end
        )
        if limit:
            df = df.head(limit)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- Main Dashboard ---
users = new_users = sessions = bounce = avg_sess = users_time = top_pages = sources = geo = devices = pd.DataFrame()

if st.session_state['creds_path'] and st.session_state['property_id']:
    col1, col2, col3, col4, col5 = st.columns(5)
    # 1. Key Metrics
    with col1:
        users = safe_run_query(["totalUsers"], [], None, None)
        st.metric("Users", users["totalUsers"].astype(int).sum() if not users.empty else "-")
    with col2:
        new_users = safe_run_query(["newUsers"], [], None, None)
        st.metric("New Users", new_users["newUsers"].astype(int).sum() if not new_users.empty else "-")
    with col3:
        sessions = safe_run_query(["sessions"], [], None, None)
        st.metric("Sessions", sessions["sessions"].astype(int).sum() if not sessions.empty else "-")
    with col4:
        bounce = safe_run_query(["bounceRate"], [], None, None)
        st.metric("Bounce Rate", f"{float(bounce['bounceRate'].iloc[0]):.2f}%" if not bounce.empty else "-")
    with col5:
        avg_sess = safe_run_query(["averageSessionDuration"], [], None, None)
        st.metric("Avg. Session Duration", f"{float(avg_sess['averageSessionDuration'].iloc[0])/60:.2f} min" if not avg_sess.empty else "-")

    st.markdown("---")
    # 2. Time Series
    st.subheader("Users Over Time")
    users_time = safe_run_query(["totalUsers"], ["date"], None, None)
    if not users_time.empty:
        users_time["date"] = pd.to_datetime(users_time["date"])
        st.line_chart(users_time.set_index("date")["totalUsers"].astype(int))
    else:
        st.info("No user data for this period.")

    # 3. Top Pages
    st.subheader("Top Pages by Pageviews")
    top_pages = safe_run_query(["screenPageViews"], ["pagePath"], None, None, limit=10)
    if not top_pages.empty:
        st.dataframe(top_pages)
        st.download_button("Download Top Pages CSV", top_pages.to_csv(index=False), "top_pages.csv", "text/csv")
    else:
        st.info("No pageview data.")

    # 4. Traffic Sources
    st.subheader("Top Traffic Sources")
    sources = safe_run_query(["sessions"], ["sessionSource"], None, None, limit=10)
    if not sources.empty:
        st.bar_chart(sources.set_index("sessionSource")["sessions"].astype(int))
        st.dataframe(sources)
        st.download_button("Download Sources CSV", sources.to_csv(index=False), "sources.csv", "text/csv")
    else:
        st.info("No source data.")

    # 5. Geography
    st.subheader("Top Countries")
    geo = safe_run_query(["sessions"], ["country"], None, None, limit=10)
    if not geo.empty:
        st.bar_chart(geo.set_index("country")["sessions"].astype(int))
        st.dataframe(geo)
        st.download_button("Download Countries CSV", geo.to_csv(index=False), "countries.csv", "text/csv")
    else:
        st.info("No country data.")

    # 6. Devices
    st.subheader("Device Category Breakdown")
    devices = safe_run_query(["sessions"], ["deviceCategory"], None, None)
    if not devices.empty:
        st.bar_chart(devices.set_index("deviceCategory")["sessions"].astype(int))
        st.dataframe(devices)
        st.download_button("Download Devices CSV", devices.to_csv(index=False), "devices.csv", "text/csv")
    else:
        st.info("No device data.")

    st.markdown("---")

    # --- Query Section ---
    st.header("Ask a Custom Question (Natural Language Query)")
    st.markdown("You can ask about any GA4 metric or dimension. [See full schema](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)")
    if st.button("Show valid GA4 fields"):
        st.info("**Metrics:** totalUsers, newUsers, sessions, bounceRate, averageSessionDuration, screenPageViews, engagedSessions, engagementRate, eventCount, conversions, userEngagementDuration, activeUsers, sessionConversionRate, userConversionRate, views\n**Dimensions:** date, pagePath, landingPage, sessionSource, sessionMedium, country, city, deviceCategory, browser, operatingSystem, language, userGender, userAgeBracket, eventName, sessionDefaultChannelGroup, region, continent, platform, appVersion, pageTitle, sourceMedium, campaignName, hostName")
    user_query = st.text_input("Type your question (e.g. 'Show me users from the US'):")
    if user_query:
        if not st.session_state['openai_api_key']:
            st.warning("Please enter your OpenAI API key in the sidebar to use natural language queries.")
        else:
            with st.spinner("Processing your query..."):
                try:
                    params = nlq_to_ga4_params(user_query, st.session_state['openai_api_key'])
                except Exception as e:
                    st.error(f"OpenAI API error: {e}")
                    st.info("Check your API key or try again later.")
                    params = None
                if params:
                    if 'rephrase' in params:
                        st.warning(f"We couldn't understand your question. Try rephrasing as: '{params['rephrase']}'")
                    elif 'error' in params:
                        st.error(params['error'])
                        st.info("Try rephrasing your question or use the 'Show valid GA4 fields' button above.")
                    else:
                        try:
                            df = run_ga4_query(
                                st.session_state['property_id'],
                                st.session_state['creds_path'],
                                params['metrics'],
                                params['dimensions'],
                                DEFAULT_START,
                                DEFAULT_END
                            )
                            if df.empty:
                                st.warning("No data returned for this query.")
                            else:
                                st.write(params.get('summary', ''))
                                st.dataframe(df)
                                st.download_button("Download Query Result CSV", df.to_csv(index=False), "query_result.csv", "text/csv")
                        except Exception as e:
                            st.error(f"Error fetching GA4 data: {e}")
                            st.info("Try rephrasing your question or use the 'Show valid GA4 fields' button above.")

    # --- Download All Data as ZIP ---
    st.markdown("---")
    st.subheader("Download All Dashboard Data")
    if st.button("Download All as ZIP"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            if not users.empty:
                zf.writestr("users.csv", users.to_csv(index=False))
            if not new_users.empty:
                zf.writestr("new_users.csv", new_users.to_csv(index=False))
            if not sessions.empty:
                zf.writestr("sessions.csv", sessions.to_csv(index=False))
            if not bounce.empty:
                zf.writestr("bounce_rate.csv", bounce.to_csv(index=False))
            if not avg_sess.empty:
                zf.writestr("avg_session_duration.csv", avg_sess.to_csv(index=False))
            if not users_time.empty:
                zf.writestr("users_time.csv", users_time.to_csv(index=False))
            if not top_pages.empty:
                zf.writestr("top_pages.csv", top_pages.to_csv(index=False))
            if not sources.empty:
                zf.writestr("sources.csv", sources.to_csv(index=False))
            if not geo.empty:
                zf.writestr("countries.csv", geo.to_csv(index=False))
            if not devices.empty:
                zf.writestr("devices.csv", devices.to_csv(index=False))
        zip_buffer.seek(0)
        st.download_button("Download ZIP", zip_buffer, "ga4_dashboard_data.zip", "application/zip")

    st.caption("All data is live from your GA4 property. Download any table as CSV or all as ZIP. Built with Streamlit.")
else:
    st.info("Please upload credentials and enter property ID in the sidebar.") 