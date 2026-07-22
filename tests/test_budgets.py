import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import connection
from agent.graph import run_agent
from db.models import set_budget, get_budget


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_budget.db"
    monkeypatch.setattr(connection, "DB_PATH", test_db_path)
    connection.init_db()
    connection.ensure_user("test_user")
    yield


def test_set_budget_directly(temp_db):
    set_budget("test_user", "Food", 3000)
    assert get_budget("test_user", "Food") == 3000


def test_set_budget_via_agent(temp_db):
    result = run_agent("test_user", "set my food budget to 3000")
    assert get_budget("test_user", "Food") == 3000
    assert "3000" in result["response"]


def test_budget_alert_triggers_near_limit(temp_db):
    set_budget("test_user", "Food", 100)
    run_agent("test_user", "fries 90")
    result = run_agent("test_user", "coffee 5")
    assert "budget" in result["response"].lower()


def test_budget_alert_triggers_over_limit(temp_db):
    set_budget("test_user", "Food", 50)
    result = run_agent("test_user", "expensive lunch 100")
    assert "over" in result["response"].lower()