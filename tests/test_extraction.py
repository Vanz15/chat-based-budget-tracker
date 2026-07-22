"""
Phase 2 tests: LLM extraction layer.
Run with: python -m pytest tests/test_extraction.py -v

Note: these tests make real Groq API calls (no mocking), since the whole
point of Phase 2 is verifying the model's actual behavior. This means:
- Tests require GROQ_API_KEY to be set (via .env)
- Tests are slower than typical unit tests
- Results could vary slightly between runs since it's a live model
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.extraction import extract_transaction, CATEGORIES


def test_simple_dollar_format():
    result = extract_transaction("fries $2")
    assert result["item"].lower() == "fries"
    assert result["amount"] == 2.0
    assert result["category"] == "Food"


def test_sentence_format():
    result = extract_transaction("i bought fries for $2")
    assert result["amount"] == 2.0
    assert result["category"] == "Food"


def test_no_currency_symbol():
    result = extract_transaction("coffee 150")
    assert result["amount"] == 150.0
    assert result["category"] == "Food"


def test_peso_word_format():
    result = extract_transaction("grabbed a haircut, 250 pesos")
    assert result["amount"] == 250.0
    assert result["category"] == "Personal Care"


def test_bills_category():
    result = extract_transaction("paid 1200 for electricity bill")
    assert result["amount"] == 1200.0
    assert result["category"] == "Bills"


def test_shopping_category():
    result = extract_transaction("bought a phone case for 350")
    assert result["amount"] == 350.0
    assert result["category"] == "Shopping"


def test_category_always_valid():
    """Whatever category the model picks, it must be from our fixed list."""
    result = extract_transaction("bought a rubber duck for 99")
    assert result is not None
    assert result["category"] in CATEGORIES


def test_amount_is_always_positive_number():
    result = extract_transaction("lunch 85")
    assert isinstance(result["amount"], float)
    assert result["amount"] > 0


def test_returns_all_required_fields():
    result = extract_transaction("taxi ride 120")
    assert "item" in result
    assert "amount" in result
    assert "category" in result

def test_non_purchase_message_returns_none():
    result = extract_transaction("hi")
    assert result is None

def test_non_purchase_never_returns_zero_amount():
    """Regression test: 'hi' must never produce a transaction with amount 0,
    whether by not calling the tool or by the defensive amount<=0 check."""
    result = extract_transaction("hi")
    assert result is None


def test_greeting_variants_all_return_none():
    for msg in ["hi", "hello", "how are you", "what can you do"]:
        result = extract_transaction(msg)
        assert result is None, f"Expected None for '{msg}', got {result}"

def test_correction_message_not_treated_as_purchase():
    assert extract_transaction("actually that was 100") is None

def test_correction_variants_not_treated_as_purchase():
    for msg in ["it was 50 not 5", "change that to 200", "that should be 30"]:
        result = extract_transaction(msg)
        assert result is None, f"Expected None for '{msg}', got {result}"

def test_explicit_usd_keyword_overrides_model():
    result = extract_transaction("book for 10 USD")
    assert result["currency"] == "USD"

def test_dollar_word_detected():
    result = extract_transaction("bought coffee for 5 dollars")
    assert result["currency"] == "USD"