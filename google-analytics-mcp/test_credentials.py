import os
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient

# Set credentials path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/service-account-key.json"  # <-- Set your own credentials path here
os.environ["GA4_PROPERTY_ID"] = "property"

try:
    # Test connection
    client = BetaAnalyticsDataClient()
    print("✅ GA4 credentials working!")
    print(f"✅ Using credentials: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
    print(f"✅ Property ID: {os.environ['GA4_PROPERTY_ID']}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 