import pandas as pd
from src.database import get_connection
from datetime import datetime

# ── Default limits (used only when no user-saved limit exists) ──
DEFAULT_LIMITS = {
    "Food":          5000,
    "Transport":     3000,
    "Rent":          10000,
    "Shopping":      4000,
    "Entertainment": 3000,
    "Others":        2000,
}


# ═══════════════════════════════════════════════
#  PERSISTENT LIMIT STORAGE  (table: category_limits)
# ═══════════════════════════════════════════════

def _ensure_limits_table():
    """Create the category_limits table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS category_limits (
            category TEXT PRIMARY KEY,
            monthly_limit REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_limits() -> dict:
    """
    Return the current monthly limits for every category.
    Falls back to DEFAULT_LIMITS for any category not yet saved by the user.
    """
    _ensure_limits_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, monthly_limit FROM category_limits")
    rows = cursor.fetchall()
    conn.close()

    limits = dict(DEFAULT_LIMITS)          # start with defaults
    for cat, val in rows:
        limits[cat] = val                  # override with user values
    return limits


def save_limits(limits: dict):
    """
    Persist a {category: amount} dict to the DB.
    Uses INSERT OR REPLACE so it works for both first-save and updates.
    """
    _ensure_limits_table()
    conn = get_connection()
    for cat, val in limits.items():
        conn.execute(
            "INSERT OR REPLACE INTO category_limits (category, monthly_limit) VALUES (?, ?)",
            (cat, float(val))
        )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════
#  REPORT  (uses live user limits)
# ═══════════════════════════════════════════════

def overspending_report() -> str:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()

    if df.empty:
        return "No expenses found."

    df["date"] = pd.to_datetime(df["date"])
    current_month = datetime.now().strftime("%Y-%m")
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df = df[df["month"] == current_month]

    limits = get_limits()
    report = "\n🚨 Overspending Report\n\n"
    for cat, limit in limits.items():
        spent = float(df[df["category"] == cat]["amount"].sum())
        if spent > limit:
            report += f"⚠ {cat}: ₹{spent:,.0f} / ₹{limit:,}\n"
        else:
            report += f"✔ {cat}: ₹{spent:,.0f} / ₹{limit:,}\n"
    return report


def check_overspending() -> list:
    """
    Returns a list of alert strings for every category that has exceeded
    its monthly limit in the current month.
    Returns an empty list when nothing is over the limit.
    """
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()

    if df.empty:
        return []

    df["date"] = pd.to_datetime(df["date"])
    current_month = datetime.now().strftime("%Y-%m")
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df = df[df["month"] == current_month]

    limits = get_limits()
    alerts = []
    for cat, limit in limits.items():
        spent = float(df[df["category"] == cat]["amount"].sum())
        if spent > limit:
            alerts.append(
                f"⚠  {cat} over limit!   ₹{spent:,.0f} / ₹{limit:,}"
            )
    return alerts