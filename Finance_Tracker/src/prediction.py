import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from src.database import get_connection


def predict_next_month_expense():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()

    if df.empty:
        raise ValueError("No expenses recorded yet. Add some expenses first.")

    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    monthly = df.groupby("month")["amount"].sum().reset_index()

    # ── Fallback: only 1 month of data ──────────────────────────────────────
    # Instead of raising an error, return the average daily spend × 30
    # as a reasonable next-month estimate.
    if len(monthly) < 2:
        total_days = max((df["date"].max() - df["date"].min()).days, 1)
        daily_avg = df["amount"].sum() / total_days
        return max(float(daily_avg * 30), float(df["amount"].sum()))

    # ── Normal path: linear regression over monthly totals ──────────────────
    X = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly["amount"].values

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict([[len(monthly)]])[0]
    return max(prediction, 0)