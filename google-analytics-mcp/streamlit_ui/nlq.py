import language_model_api as lm
import json
from ga4_fields import GA4_METRICS, GA4_DIMENSIONS, UA_TO_GA4

def validate_fields(fields, valid_set, mapping):
    valid = []
    invalid = []
    for f in fields:
        if f in valid_set:
            valid.append(f)
        elif f in mapping:
            valid.append(mapping[f])
        else:
            invalid.append(f)
    return valid, invalid

def nlq_to_ga4_params(nl_query, api_key):
    lm.api_key = api_key
    prompt = f"""
You are an expert Google Analytics 4 assistant for a tech company. Your job is to analyze and translate ANY custom user query about their website's analytics into valid Google Analytics 4 API parameters. Do NOT copy or repeat examples. Instead, always analyze the user's question and generate the correct metrics, dimensions, and filters for a live GA4 API call.

Only use dimensions and metrics from the following lists. Do not use any other fields.
Metrics: {GA4_METRICS}
Dimensions: {GA4_DIMENSIONS}

For the question: '{nl_query}'
If the question is ambiguous, unclear, or cannot be answered directly, respond with a JSON object with a 'rephrase' key containing a suggested, valid rephrasing of the question that would work. Otherwise, respond with a JSON object with keys: metrics (list), dimensions (list), filters (dict, optional), and a summary (string). Do NOT include date_range_start or date_range_end unless the user specifically asks for a time period. Default to site-wide or most recent data if no date is given.

Here are some EXAMPLES (for guidance only, do NOT copy):
Q: How many users?
A: {{"metrics": ["totalUsers"], "dimensions": [], "summary": "Total users for the site (all time or most recent data)."}}
Q: Top 5 pages by pageviews
A: {{"metrics": ["screenPageViews"], "dimensions": ["pagePath"], "summary": "Top 5 pages by pageviews (all time or most recent data)."}}
Q: What is the bounce rate?
A: {{"metrics": ["bounceRate"], "dimensions": [], "summary": "Bounce rate for the site (all time or most recent data)."}}
Q: How many users from the United States?
A: {{"metrics": ["totalUsers"], "dimensions": ["country"], "filters": {{"country": "United States"}}, "summary": "Total users from the United States (all time or most recent data)."}}
Q: How many blue widgets did we sell?
A: {{"rephrase": "How many conversions for the 'blue widget' event?"}}

Now, analyze the user's question and output the correct JSON for a live GA4 API call:
"""
    try:
        response = lm.ChatCompletion.create(
            model="best-available-nlq-model",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0
        )
        content = response.choices[0].message.content.strip()
        if not content:
            return {"error": "Language model API returned an empty response. Please check your API key, usage limits, or try again later."}
        try:
            params = json.loads(content)
        except Exception:
            return {"error": "Language model API returned an invalid response. This may be a temporary issue with the API. Please try again, check your API key, or contact support if the problem persists."}
        if 'rephrase' in params:
            return {"rephrase": params['rephrase']}
        # Validate metrics and dimensions
        metrics, invalid_metrics = validate_fields(params.get("metrics", []), GA4_METRICS, UA_TO_GA4)
        dimensions, invalid_dims = validate_fields(params.get("dimensions", []), GA4_DIMENSIONS, UA_TO_GA4)
        errors = []
        if invalid_metrics:
            errors.append(f"Invalid metrics: {invalid_metrics}")
        if invalid_dims:
            errors.append(f"Invalid dimensions: {invalid_dims}")
        if errors:
            return {"error": " ".join(errors) + ". Please use only valid GA4 fields."}
        params["metrics"] = metrics
        params["dimensions"] = dimensions
        return params
    except Exception as e:
        return {"error": f"Language model API error: {e}. Please check your API key, usage limits, or try again later."} 