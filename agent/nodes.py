from agent.state import AgentState
from llm.extraction import extract_transaction
from db.models import insert_transaction


def add_transaction_node(state: AgentState) -> AgentState:
    """Extracts item/amount/category from the raw message, inserts it into
    the DB, and writes a plain confirmation response back into state.
    No tone personalization yet — that's Phase 5."""
    extracted = extract_transaction(state["message"])

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
    state["response"] = (
        f"Logged: {extracted['item']} — ${extracted['amount']:.2f} "
        f"({extracted['category']})"
    )
    return state