"""
Phase 3 tests: agent loop (extraction + DB insert wired together).
Run with: python -m pytest tests/test_agent.py -v

These tests make real Groq API calls and write to a temporary DB.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import connection
from agent.graph import run_agent


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Same pattern as Phase 1 tests — isolate every test from real data."""
    test_db_path = tmp_path / "test_budget.db"
    monkeypatch.setattr(connection, "DB_PATH", test_db_path)
    connection.init_db()
    connection.ensure_user("test_user")
    yield


def test_add_transaction_end_to_end(temp_db):
    result = run_agent("test_user", "fries $2")

    assert result["item"].lower() == "fries"
    assert result["amount"] == 2.0
    assert result["category"] == "Food"
    assert result["transaction_id"] is not None
    assert "Logged" in result["response"]


def test_transaction_actually_persists_in_db(temp_db):
    from db.models import get_recent_transactions

    run_agent("test_user", "coffee 150")
    txs = get_recent_transactions("test_user")

    assert len(txs) == 1
    assert txs[0]["item"].lower() == "coffee"
    assert txs[0]["amount"] == 150.0


def test_multiple_messages_create_multiple_rows(temp_db):
    from db.models import get_recent_transactions

    run_agent("test_user", "fries $2")
    run_agent("test_user", "taxi ride 120")
    run_agent("test_user", "paid 1200 for electricity bill")

    txs = get_recent_transactions("test_user")
    assert len(txs) == 3


def test_response_contains_amount_and_category(temp_db):
    result = run_agent("test_user", "bought a phone case for 350")
    assert "350" in result["response"]
    assert "Shopping" in result["response"]