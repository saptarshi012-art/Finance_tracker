import pandas as pd
from src.database import get_connection
from datetime import datetime, timedelta


def generate_insights() -> str:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()

    if df.empty:
        return "No data yet — add your first expense to unlock smart insights."

    df["date"]  = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    df["week"]  = df["date"].dt.isocalendar().week
    df["dow"]   = df["date"].dt.day_name()

    now           = pd.Timestamp(datetime.now())
    current_month = now.to_period("M")
    prev_month    = (now - pd.DateOffset(months=1)).to_period("M")

    cur  = df[df["month"] == current_month]
    prev = df[df["month"] == prev_month]

    insights = []

    # ── 1. Month-over-month spending change ──────────────────────────
    if not cur.empty and not prev.empty:
        cur_total  = cur["amount"].sum()
        prev_total = prev["amount"].sum()
        pct_change = ((cur_total - prev_total) / prev_total) * 100
        if pct_change > 15:
            insights.append(
                f"📈 Spending is up {pct_change:.0f}% vs last month "
                f"(₹{cur_total:,.0f} vs ₹{prev_total:,.0f}). Consider reviewing your budget."
            )
        elif pct_change < -15:
            insights.append(
                f"📉 Great discipline! Spending dropped {abs(pct_change):.0f}% vs last month "
                f"(₹{cur_total:,.0f} vs ₹{prev_total:,.0f})."
            )
        else:
            insights.append(
                f"📊 Spending is steady this month — {pct_change:+.0f}% vs last month."
            )

    # ── 2. Fastest-growing category ─────────────────────────────────
    if not cur.empty and not prev.empty:
        cur_cat  = cur.groupby("category")["amount"].sum()
        prev_cat = prev.groupby("category")["amount"].sum()
        common   = cur_cat.index.intersection(prev_cat.index)
        if len(common):
            growth = ((cur_cat[common] - prev_cat[common]) / prev_cat[common]) * 100
            top    = growth.idxmax()
            if growth[top] > 20:
                insights.append(
                    f"🔺 {top} spending surged {growth[top]:.0f}% this month — "
                    f"₹{cur_cat[top]:,.0f} vs ₹{prev_cat[top]:,.0f} last month."
                )

    # ── 3. Single largest transaction ────────────────────────────────
    if not df.empty:
        top_row  = df.loc[df["amount"].idxmax()]
        insights.append(
            f"💸 Biggest single expense: ₹{top_row['amount']:,.0f} on "
            f"'{top_row['description']}' ({top_row['category']})."
        )

    # ── 4. Most expensive day of the week ────────────────────────────
    if len(df) >= 5:
        dow_avg = df.groupby("dow")["amount"].mean()
        peak    = dow_avg.idxmax()
        insights.append(
            f"📅 You spend the most on {peak}s on average "
            f"(₹{dow_avg[peak]:,.0f}/transaction). Plan ahead for that day."
        )

    # ── 5. Budget burn-rate — will you overshoot this month? ─────────
    if not cur.empty:
        day_of_month  = now.day
        days_in_month = (now + pd.offsets.MonthEnd(0)).day
        days_left     = days_in_month - day_of_month
        daily_rate    = cur["amount"].sum() / day_of_month
        projected     = daily_rate * days_in_month
        if days_left > 0:
            insights.append(
                f"🔮 At your current daily rate of ₹{daily_rate:,.0f}, "
                f"you're on track to spend ₹{projected:,.0f} by month-end "
                f"({days_left} days left)."
            )

    # ── 6. Frequency alert — category with most transactions ─────────
    if not cur.empty and len(cur) >= 3:
        freq_cat = cur["category"].value_counts().idxmax()
        freq_cnt = cur["category"].value_counts().max()
        insights.append(
            f"🔁 You made {freq_cnt} {freq_cat} transactions this month — "
            f"your most frequent spending category."
        )

    # ── 7. Small-spend leak detection ────────────────────────────────
    if len(df) >= 10:
        small     = df[df["amount"] < df["amount"].quantile(0.25)]
        small_sum = small["amount"].sum()
        small_cnt = len(small)
        if small_cnt >= 5:
            insights.append(
                f"☕ Small expenses add up: {small_cnt} transactions under "
                f"₹{df['amount'].quantile(0.25):,.0f} total ₹{small_sum:,.0f}."
            )

    # ── 8. Savings window — quietest spending week ───────────────────
    if len(df) >= 7:
        week_total = df.groupby("week")["amount"].sum()
        best_week  = week_total.idxmin()
        insights.append(
            f"✅ Your most frugal week was Week {best_week} "
            f"(₹{week_total[best_week]:,.0f} total). Aim to repeat it!"
        )

    # ── 9. Category diversity ────────────────────────────────────────
    if not cur.empty:
        n_cats = cur["category"].nunique()
        if n_cats == 1:
            insights.append(
                f"🎯 All spending this month is in one category: "
                f"{cur['category'].iloc[0]}. Diversify to track better."
            )
        elif n_cats >= 5:
            insights.append(
                f"🌐 Spending spread across {n_cats} categories this month — "
                f"good coverage for tracking."
            )

    # ── 10. Recent 7-day vs prior 7-day ─────────────────────────────
    last7  = df[df["date"] >= now - timedelta(days=7)]["amount"].sum()
    prior7 = df[(df["date"] >= now - timedelta(days=14)) &
                (df["date"] <  now - timedelta(days=7))]["amount"].sum()
    if last7 > 0 and prior7 > 0:
        delta = ((last7 - prior7) / prior7) * 100
        arrow = "⬆" if delta > 0 else "⬇"
        insights.append(
            f"{arrow} Last 7 days: ₹{last7:,.0f} — "
            f"{'up' if delta > 0 else 'down'} {abs(delta):.0f}% vs the 7 days before."
        )

    # ── Fallback ─────────────────────────────────────────────────────
    if not insights:
        return "Add more expenses across multiple days to unlock detailed insights."

    return "\n\n".join(f"  {line}" for line in insights)