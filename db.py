import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".budget_tracker.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_limit REAL NOT NULL
            );
        """)


def get_transactions(year=None, month=None, category=None):
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    if year and month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(f"{year:04d}-{month:02d}")
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY date DESC"
    with get_conn() as conn:
        return conn.execute(query, params).fetchall()


def get_transaction(tx_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (tx_id,)
        ).fetchone()


def add_transaction(date, description, amount, category):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date, description, amount, category),
        )


def update_transaction(tx_id, date, description, amount, category):
    with get_conn() as conn:
        conn.execute(
            "UPDATE transactions SET date=?, description=?, amount=?, category=? WHERE id=?",
            (date, description, amount, category, tx_id),
        )


def delete_transaction(tx_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM transactions WHERE id=?", (tx_id,))


def get_categories():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM transactions ORDER BY category"
        ).fetchall()
        return [r["category"] for r in rows]


def get_monthly_balance(year, month):
    with get_conn() as conn:
        result = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions "
            "WHERE strftime('%Y-%m', date) = ?",
            (f"{year:04d}-{month:02d}",),
        ).fetchone()
        return result["total"]


def get_monthly_summary(year, month):
    """Returns rows of (category, income, spent, monthly_limit) for the month."""
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT
                t.category,
                COALESCE(SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END), 0) AS income,
                COALESCE(ABS(SUM(CASE WHEN t.amount < 0 THEN t.amount ELSE 0 END)), 0) AS spent,
                b.monthly_limit
            FROM transactions t
            LEFT JOIN budgets b ON t.category = b.category
            WHERE strftime('%Y-%m', t.date) = ?
            GROUP BY t.category
            ORDER BY t.category
            """,
            (f"{year:04d}-{month:02d}",),
        ).fetchall()


def get_budget_warnings(year, month):
    """Returns list of (category, spent, limit, over_by) for over-budget categories."""
    rows = get_monthly_summary(year, month)
    warnings = []
    for r in rows:
        if r["monthly_limit"] and r["spent"] > r["monthly_limit"]:
            warnings.append({
                "category": r["category"],
                "spent": r["spent"],
                "limit": r["monthly_limit"],
                "over_by": r["spent"] - r["monthly_limit"],
            })
    return warnings


def get_budgets():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM budgets ORDER BY category").fetchall()


def set_budget(category, limit):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO budgets (category, monthly_limit) VALUES (?, ?)",
            (category, limit),
        )


def delete_budget(category):
    with get_conn() as conn:
        conn.execute("DELETE FROM budgets WHERE category=?", (category,))


def get_spending_by_category(year, month):
    """Returns list of (category, total_spent) for expenses in the month."""
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT category, ABS(SUM(amount)) AS total
            FROM transactions
            WHERE strftime('%Y-%m', date) = ? AND amount < 0
            GROUP BY category
            ORDER BY total DESC
            """,
            (f"{year:04d}-{month:02d}",),
        ).fetchall()


def get_monthly_totals(num_months=6):
    """Returns last N months with income and expense totals, oldest first."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT strftime('%Y-%m', date) AS month,
                   COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS income,
                   COALESCE(ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)), 0) AS expenses
            FROM transactions
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
            """,
            (num_months,),
        ).fetchall()
        return list(reversed(rows))
