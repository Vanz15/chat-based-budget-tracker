import psycopg2
from db.connection import get_connection, release_connection


def insert_transaction(user_id: str, raw_text: str, item: str, amount: float, category: str) -> int:
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if not item or not category:
        raise ValueError("item and category cannot be empty")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO transactions (user_id, raw_text, item, amount, category)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
                """,
                (user_id, raw_text, item, amount, category),
            )
            new_id = cur.fetchone()["id"]
        conn.commit()
        return new_id
    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"Failed to insert transaction: {e}") from e
    finally:
        release_connection(conn)


def get_recent_transactions(user_id: str, limit: int = 10):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, item, amount, category, tx_timestamp
                FROM transactions WHERE user_id = %s
                ORDER BY tx_timestamp DESC LIMIT %s
                """,
                (user_id, limit),
            )
            rows = cur.fetchall()
        transactions = [dict(row) for row in rows]
        for t in transactions:
            if hasattr(t.get("tx_timestamp"), "strftime"):
                t["tx_timestamp"] = t["tx_timestamp"].strftime("%Y-%m-%d %H:%M")
        return transactions
    except psycopg2.Error as e:
        raise RuntimeError(f"Failed to fetch transactions: {e}") from e
    finally:
        release_connection(conn)


def get_user_tone(user_id: str) -> str:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT tone_pref FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
        return row["tone_pref"] if row else "neutral"
    finally:
        release_connection(conn)


def set_user_tone(user_id: str, tone: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET tone_pref = %s WHERE id = %s", (tone, user_id))
        conn.commit()
    finally:
        release_connection(conn)


def get_transaction_by_id(tx_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, item, amount, category, tx_timestamp FROM transactions WHERE id = %s",
                (tx_id,),
            )
            row = cur.fetchone()
        return dict(row) if row else None
    finally:
        release_connection(conn)


def find_best_match_transaction(user_id: str, item_hint: str = None, limit: int = 5):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT id, item, amount, category, tx_timestamp FROM transactions WHERE user_id = %s"
            params = [user_id]
            if item_hint:
                query += " AND item ILIKE %s"
                params.append(f"%{item_hint}%")
            query += " ORDER BY tx_timestamp DESC LIMIT %s"
            params.append(limit)
            cur.execute(query, params)
            rows = cur.fetchall()
        transactions = [dict(row) for row in rows]
        for t in transactions:
            if hasattr(t.get("tx_timestamp"), "strftime"):
                t["tx_timestamp"] = t["tx_timestamp"].strftime("%Y-%m-%d %H:%M")
        return transactions
    finally:
        release_connection(conn)


def update_transaction(tx_id: int, item: str = None, amount: float = None, category: str = None):
    if amount is not None and amount <= 0:
        raise ValueError("amount must be positive")
    conn = get_connection()
    try:
        fields, params = [], []
        if item is not None:
            fields.append("item = %s"); params.append(item)
        if amount is not None:
            fields.append("amount = %s"); params.append(amount)
        if category is not None:
            fields.append("category = %s"); params.append(category)
        if not fields:
            return
        params.append(tx_id)
        with conn.cursor() as cur:
            cur.execute(f"UPDATE transactions SET {', '.join(fields)} WHERE id = %s", params)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"Failed to update transaction: {e}") from e
    finally:
        release_connection(conn)


def delete_transaction(tx_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM transactions WHERE id = %s", (tx_id,))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"Failed to delete transaction: {e}") from e
    finally:
        release_connection(conn)


def query_transactions(user_id: str, category: str = None, category_mode: str = "include",
                        start_date: str = None, end_date: str = None, limit: int = None,
                        item_hint: str = None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT item, amount, category, tx_timestamp FROM transactions WHERE user_id = %s"
            params = [user_id]

            if item_hint:
                query += " AND item ILIKE %s"
                params.append(f"%{item_hint}%")
            if category:
                query += " AND category != %s" if category_mode == "exclude" else " AND category = %s"
                params.append(category)
            if start_date:
                query += " AND tx_timestamp::date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND tx_timestamp::date <= %s"
                params.append(end_date)

            query += " ORDER BY tx_timestamp DESC"
            if limit:
                query += " LIMIT %s"
                params.append(limit)

            cur.execute(query, params)
            rows = cur.fetchall()
        transactions = [dict(row) for row in rows]
        for t in transactions:
            t["amount"] = float(t["amount"])
            if hasattr(t.get("tx_timestamp"), "strftime"):
                t["tx_timestamp"] = t["tx_timestamp"].strftime("%Y-%m-%d %H:%M")
        total = sum(t["amount"] for t in transactions)
        return {"transactions": transactions, "total": total, "count": len(transactions)}
    except psycopg2.Error as e:
        raise RuntimeError(f"Failed to query transactions: {e}") from e
    finally:
        release_connection(conn)


def set_budget(user_id: str, category: str, limit_amount: float, period: str = "monthly"):
    if limit_amount <= 0:
        raise ValueError("limit_amount must be positive")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO budgets (user_id, category, limit_amount, period)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, category, period)
                DO UPDATE SET limit_amount = EXCLUDED.limit_amount
                """,
                (user_id, category, limit_amount, period),
            )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"Failed to set budget: {e}") from e
    finally:
        release_connection(conn)


def get_budget(user_id: str, category: str, period: str = "monthly"):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT limit_amount FROM budgets WHERE user_id=%s AND category=%s AND period=%s",
                (user_id, category, period),
            )
            row = cur.fetchone()
        return float(row["limit_amount"]) if row else None
    finally:
        release_connection(conn)


def get_month_spent(user_id: str, category: str):
    from datetime import date
    start_of_month = date.today().replace(day=1).isoformat()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(SUM(amount), 0) as total FROM transactions
                WHERE user_id=%s AND category=%s AND tx_timestamp::date >= %s
                """,
                (user_id, category, start_of_month),
            )
            row = cur.fetchone()
        return float(row["total"])
    finally:
        release_connection(conn)


def log_interaction(user_id: str, raw_message: str, intent: str, extracted: dict, response: str):
    import json as json_module
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO interaction_log (user_id, raw_message, intent, extracted_json, response)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, raw_message, intent, json_module.dumps(extracted) if extracted else None, response),
            )
        conn.commit()
    except Exception:
        pass
    finally:
        release_connection(conn)

def get_all_budgets_and_spending(user_id: str, categories: list):
    """Single round trip: returns {category: {limit, spent}} for every
    category at once, instead of 16 separate calls."""
    from datetime import date
    start_of_month = date.today().replace(day=1).isoformat()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT category, limit_amount FROM budgets WHERE user_id = %s AND period = 'monthly'",
                (user_id,),
            )
            budget_rows = {row["category"]: float(row["limit_amount"]) for row in cur.fetchall()}

            cur.execute(
                """
                SELECT category, COALESCE(SUM(amount), 0) as total
                FROM transactions
                WHERE user_id = %s AND tx_timestamp::date >= %s
                GROUP BY category
                """,
                (user_id, start_of_month),
            )
            spent_rows = {row["category"]: float(row["total"]) for row in cur.fetchall()}

        return {
            cat: {"limit": budget_rows.get(cat), "spent": spent_rows.get(cat, 0.0)}
            for cat in categories
        }
    finally:
        release_connection(conn)