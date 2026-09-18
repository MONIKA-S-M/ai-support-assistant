import pandas as pd

DATA_PATH = "data/support_tickets.csv"


def load_data():
    """Load and prepare the support ticket dataset."""
    df = pd.read_csv(DATA_PATH)

    # Convert created_at to datetime
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    # Keep the original missing values.
    # Pandas calculations will ignore NaN values where appropriate.

    return df