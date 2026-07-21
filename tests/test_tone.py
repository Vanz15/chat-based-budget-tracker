import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.tone import generate_comment, VALID_TONES, generate_fallback_reply


@pytest.mark.parametrize("tone", VALID_TONES)
def test_generate_comment_returns_nonempty_string(tone):
    comment = generate_comment("fries", 2.0, "Food", "PHP", tone)
    assert isinstance(comment, str)
    assert len(comment) > 0


def test_invalid_tone_falls_back_to_neutral():
    comment = generate_comment("fries", 2.0, "Food", "PHP", "made_up_tone")
    assert isinstance(comment, str)
    assert len(comment) > 0


def test_comment_is_reasonably_short():
    comment = generate_comment("keyboard", 1300.0, "Shopping", "PHP", "sarcastic")
    assert len(comment.split()) < 40  # loose upper bound, model isn't perfectly precise on word count




def test_fallback_reply_for_greeting():
    reply = generate_fallback_reply("hi", "neutral")
    assert isinstance(reply, str)
    assert len(reply) > 0


def test_fallback_reply_mentions_logging_purchase():
    reply = generate_fallback_reply("hello there", "neutral").lower()
    # loose check — should nudge toward the app's purpose somehow
    assert any(word in reply for word in ["log", "purchase", "spent", "buy", "bought"])