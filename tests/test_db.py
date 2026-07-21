"""
Phase 1 tests: database foundation.
Run with: python -m pytest tests/test_db.py -v
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import connection, models


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Points the DB at a temporary file so tests never touch real data/budget.db."""
    test_db_path = tmp_path / "test_budget.db"
    monkeypatch.setattr(connection, "DB_PATH", test_db_path)
    connection.init_db()
    connection.ensure_user("test_user")
    yield


def test_init_db_creates_tables(temp_db):
    conn = connection.get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = {row["name"] for row in tables}
    assert "users" in table_names
    assert "transactions" in table_names
    conn.close()


def test_ensure_user_is_idempotent(temp_db):
    connection.ensure_user("test_user")
    connection.ensure_user("test_user")
    conn = connection.get_connection()
    count = conn.execute(
        "SELECT COUNT(*) as c FROM users WHERE id = ?", ("test_user",)
    ).fetchone()["c"]
    conn.close()
    assert count == 1


def test_insert_and_read_transaction(temp_db):
    tx_id = models.insert_transaction("test_user", "fries $2", "fries", 2.0, "Food")
    assert tx_id == 1

    txs = models.get_recent_transactions("test_user")
    assert len(txs) == 1
    assert txs[0]["item"] == "fries"
    assert txs[0]["amount"] == 2.0
    assert txs[0]["category"] == "Food"


def test_insert_rejects_negative_amount(temp_db):
    with pytest.raises(ValueError):
        models.insert_transaction("test_user", "bad tx", "item", -5.0, "Food")


def test_insert_rejects_empty_item(temp_db):
    with pytest.raises(ValueError):
        models.insert_transaction("test_user", "bad tx", "", 5.0, "Food")


def test_recent_transactions_respects_limit(temp_db):
    for i in range(5):
        models.insert_transaction("test_user", f"item {i}", f"item{i}", 1.0, "Food")
    txs = models.get_recent_transactions("test_user", limit=3)
    assert len(txs) == 3


def test_transaction_requires_existing_user(temp_db):
    with pytest.raises(RuntimeError):
        models.insert_transaction("ghost", "fries $2", "fries", 2.0, "Food")