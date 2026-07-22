import os, sys, pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import connection
from agent.graph import run_agent
from db.models import get_recent_transactions

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "test.db")
    connection.init_db()
    connection.ensure_user("test_user")
    yield

def test_edit_asks_for_confirmation_not_immediate(temp_db):
    run_agent("test_user", "coffee 3")
    result = run_agent("test_user", "actually that was 30")
    assert result["pending_edit"] is not None
    txs = get_recent_transactions("test_user")
    assert txs[0]["amount"] == 3.0  # unchanged until confirmed

def test_confirmed_edit_updates_db(temp_db):
    from agent.nodes import confirm_edit_node
    run_agent("test_user", "coffee 3")
    result = run_agent("test_user", "actually that was 30")
    state = {**result}
    confirmed = confirm_edit_node(state)
    txs = get_recent_transactions("test_user")
    assert txs[0]["amount"] == 30.0