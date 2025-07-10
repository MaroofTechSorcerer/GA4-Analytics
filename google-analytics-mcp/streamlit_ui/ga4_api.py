import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest

def run_ga4_query(property_id, creds_path, metrics, dimensions, date_range_start, date_range_end):
    client = BetaAnalyticsDataClient.from_service_account_file(creds_path)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=date_range_start, end_date=date_range_end)],
    )
    response = client.run_report(request)
    data = []
    for row in response.rows:
        row_data = {}
        for i, d in enumerate(dimensions):
            row_data[d] = row.dimension_values[i].value
        for i, m in enumerate(metrics):
            row_data[m] = row.metric_values[i].value
        data.append(row_data)
    return pd.DataFrame(data) 