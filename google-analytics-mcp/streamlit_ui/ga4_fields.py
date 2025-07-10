# This is a partial list. Expand as needed for full coverage.
GA4_METRICS = [
    "totalUsers", "newUsers", "sessions", "screenPageViews", "bounceRate", "averageSessionDuration", "engagedSessions", "engagementRate", "eventCount", "conversions", "userEngagementDuration", "activeUsers", "sessionConversionRate", "userConversionRate", "views"
]

GA4_DIMENSIONS = [
    "date", "pagePath", "landingPage", "sessionSource", "sessionMedium", "country", "city", "deviceCategory", "browser", "operatingSystem", "language", "userGender", "userAgeBracket", "eventName", "sessionDefaultChannelGroup", "region", "continent", "platform", "appVersion", "pageTitle", "sourceMedium", "campaignName", "hostName"
]

# UA to GA4 mapping (expand as needed)
UA_TO_GA4 = {
    "ga:landingPagePath": "landingPage",
    "ga:pagePath": "pagePath",
    "ga:source": "sessionSource",
    "ga:medium": "sessionMedium",
    "ga:country": "country",
    "ga:city": "city",
    "ga:deviceCategory": "deviceCategory",
    "ga:browser": "browser",
    "ga:operatingSystem": "operatingSystem",
    "ga:language": "language",
    "ga:userGender": "userGender",
    "ga:userAgeBracket": "userAgeBracket",
    "ga:eventName": "eventName",
    "ga:channelGrouping": "sessionDefaultChannelGroup",
    "ga:region": "region",
    "ga:continent": "continent",
    "ga:platform": "platform",
    "ga:appVersion": "appVersion",
    "ga:pageTitle": "pageTitle",
    "ga:sourceMedium": "sourceMedium",
    "ga:campaign": "campaignName",
    "ga:hostname": "hostName",
    # Add more as needed
} 