import pandas as pd
from app.data_loader import load_data


def detect_anomalies():
    df = load_data()

    anomalies = []

    # Critical tickets that are still unresolved after 24 hours
    # High-priority unresolved tickets older than 24 hours
    latest_date = df["created_at"].max()
    age_threshold = latest_date - pd.Timedelta(hours=24)

    high_priority_unresolved = df[
        (df["priority"].str.lower().isin(["high", "critical"]))
        & (df["status"].str.lower() != "resolved")
        & (df["created_at"] < age_threshold)
]

    for _, row in high_priority_unresolved.iterrows():
        anomalies.append({
            "ticket_id": row["ticket_id"],
            "type": "High-priority unresolved ticket",
            "details": f"High-priority ticket unresolved for more than 24 hours"
        })

    # Tickets with unusually long resolution time
    resolution_threshold = df["resolution_time_hrs"].quantile(0.95)

    long_resolution = df[
        df["resolution_time_hrs"] > resolution_threshold
    ]

    for _, row in long_resolution.iterrows():
        anomalies.append({
            "ticket_id": row["ticket_id"],
            "type": "Long resolution time",
            "details": f"Resolution time of {row['resolution_time_hrs']} hours"
        })

    return anomalies

def detect_weekly_resolution_anomalies():
    df = load_data()

    latest_date = df["created_at"].max()
    week_start = latest_date - pd.Timedelta(days=7)

    week_df = df[
        (df["created_at"] >= week_start)
        & (df["created_at"] <= latest_date)
    ].copy()

    threshold = week_df["resolution_time_hrs"].quantile(0.95)

    anomalies = week_df[
        week_df["resolution_time_hrs"] > threshold
    ]

    return anomalies[
        ["ticket_id", "resolution_time_hrs"]
    ].to_dict(orient="records")