from agent.state import AgentState
from llm.extraction import extract_transaction
from llm.tone import generate_comment, generate_fallback_reply
from db.models import insert_transaction, get_user_tone


def add_transaction_node(state: AgentState) -> AgentState:
    """Extracts item/amount/category, inserts it, then generates a
    tone-matched comment on top of the plain confirmation."""
    extracted = extract_transaction(state["message"])

    if extracted is None:
        tone = get_user_tone(state["user_id"])
        try:
            state["response"] = generate_fallback_reply(state["message"], tone)
        except Exception:
            state["response"] = (
                "I didn't catch a purchase in that — try something like "
                "'coffee PHP 150' and I'll log it for you."
            )
        return state

    tx_id = insert_transaction(
        user_id=state["user_id"],
        raw_text=state["message"],
        item=extracted["item"],
        amount=extracted["amount"],
        category=extracted["category"],
    )

    state["item"] = extracted["item"]
    state["amount"] = extracted["amount"]
    state["category"] = extracted["category"]
    state["transaction_id"] = tx_id

    symbol = "₱" if extracted["currency"] == "PHP" else "$"
    tone = get_user_tone(state["user_id"])

    try:
        comment = generate_comment(
            extracted["item"], extracted["amount"],
            extracted["category"], extracted["currency"], tone,
        )
    except Exception:
        comment = ""  # if tone generation fails, still show the logged confirmation

    base = f"Logged: {extracted['item']} — {symbol}{extracted['amount']:.2f} ({extracted['category']})"
    state["response"] = f"{base}\n\n{comment}" if comment else base
    return state