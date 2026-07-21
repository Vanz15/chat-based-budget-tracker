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