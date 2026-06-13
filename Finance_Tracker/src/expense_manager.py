from src.database import get_connection
from datetime import datetime

CATEGORIES = ["Food", "Transport", "Rent", "Shopping", "Entertainment", "Others"]


def add_expense(amount, category, description="", date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if amount <= 0:
        raise ValueError("Amount must be > 0")

    if category not in CATEGORIES:
        raise ValueError("Invalid category")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (date, amount, category, description)
        VALUES (?, ?, ?, ?)
    """, (date, amount, category, description))

    conn.commit()
    conn.close()


def read_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, date, amount, category, description FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": r[0], "date": r[1], "amount": r[2], "category": r[3], "description": r[4]}
        for r in rows
    ]


def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


# ✅ NEW: UPDATE EXPENSE
def update_expense(expense_id, amount, category, description):
    if amount <= 0:
        raise ValueError("Amount must be > 0")

    if category not in CATEGORIES:
        raise ValueError("Invalid category")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET amount = ?, category = ?, description = ?
        WHERE id = ?
    """, (amount, category, description, expense_id))

    conn.commit()
    conn.close()


# ✅ NEW: SEARCH + FILTER
def filter_expenses(keyword="", category=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, date, amount, category, description FROM expenses WHERE 1=1"
    params = []

    if keyword:
        query += " AND description LIKE ?"
        params.append(f"%{keyword}%")

    if category:
        query += " AND category = ?"
        params.append(category)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": r[0], "date": r[1], "amount": r[2], "category": r[3], "description": r[4]}
        for r in rows
    ]