import sqlite3
from db.connection import get_connection


def insert_transaction(user_id: str, raw_text: str, item: str, amount: float, category: str) -> int:
    """Inserts a transaction and returns its new id.
    Raises ValueError if inputs are invalid, RuntimeError if the DB write fails."""
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if not item or not category:
        raise ValueError("item and category cannot be empty")

    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO transactions (user_id, raw_text, item, amount, category)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, raw_text, item, amount, category),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Failed to insert transaction: {e}") from e
    finally:
        conn.close()


def get_recent_transactions(user_id: str, limit: int = 10):
    """Returns the most recent transactions for a user, newest first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, item, amount, category, tx_timestamp
            FROM transactions
            WHERE user_id = ?
            ORDER BY tx_timestamp DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to fetch transactions: {e}") from e
    finally:
        conn.close()

def get_user_tone(user_id: str) -> str:
    """Returns the user's tone preference, defaulting to 'neutral'."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT tone_pref FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return row["tone_pref"] if row else "neutral"
    finally:
        conn.close()


def set_user_tone(user_id: str, tone: str):
    """Updates the user's tone preference."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET tone_pref = ? WHERE id = ?", (tone, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def query_transactions(user_id: str, category: str = None, start_date: str = None, end_date: str = None):
    """Returns matching transactions plus a total. Filters are optional —
    None means 'no filter on this field'."""
    conn = get_connection()
    try:
        query = "SELECT item, amount, category, tx_timestamp FROM transactions WHERE user_id = ?"
        params = [user_id]

        if category:
            query += " AND category = ?"
            params.append(category)
        if start_date:
            query += " AND date(tx_timestamp) >= date(?)"
            params.append(start_date)
        if end_date:
            query += " AND date(tx_timestamp) <= date(?)"
            params.append(end_date)

        query += " ORDER BY tx_timestamp DESC"
        rows = conn.execute(query, params).fetchall()
        transactions = [dict(row) for row in rows]
        total = sum(t["amount"] for t in transactions)
        return {"transactions": transactions, "total": total, "count": len(transactions)}
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to query transactions: {e}") from e
    finally:
        conn.close()

def set_budget(user_id: str, category: str, limit_amount: float, period: str = "monthly"):
    if limit_amount <= 0:
        raise ValueError("limit_amount must be positive")
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO budgets (user_id, category, limit_amount, period)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, category, period)
            DO UPDATE SET limit_amount = excluded.limit_amount
            """,
            (user_id, category, limit_amount, period),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Failed to set budget: {e}") from e
    finally:
        conn.close()


def get_budget(user_id: str, category: str, period: str = "monthly"):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT limit_amount FROM budgets WHERE user_id=? AND category=? AND period=?",
            (user_id, category, period),
        ).fetchone()
        return row["limit_amount"] if row else None
    finally:
        conn.close()


def get_month_spent(user_id: str, category: str):
    """Total spent in the given category so far this calendar month."""
    from datetime import date
    start_of_month = date.today().replace(day=1).isoformat()
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total FROM transactions
            WHERE user_id=? AND category=? AND date(tx_timestamp) >= date(?)
            """,
            (user_id, category, start_of_month),
        ).fetchone()
        return row["total"]
    finally:
        conn.close()