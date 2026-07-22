import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.intent import classify_intent


def test_purchase_message_classified_as_add_transaction():
    assert classify_intent("fries PHP 100") == "add_transaction"
    assert classify_intent("bought a phone case for 350") == "add_transaction"


def test_query_message_classified_as_query_transactions():
    assert classify_intent("how much did I spend this week") == "query_transactions"
    assert classify_intent("show my food spending") == "query_transactions"


def test_greeting_defaults_to_add_transaction():
    # relies on add_transaction_node's existing graceful fallback for non-purchases
    assert classify_intent("hi") == "add_transaction"