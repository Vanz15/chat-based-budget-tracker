from agent.state import AgentState
from llm.extraction import extract_transaction
from llm.tone import generate_comment, generate_fallback_reply
from llm.intent import classify_intent
from db.models import insert_transaction, get_user_tone


def try_extract_node(state: AgentState) -> AgentState:
    """Attempts extraction first, before any classification call. This is
    the common-case fast path: most messages ARE purchases, so we avoid
    a separate intent-classification call whenever possible."""
    extracted = extract_transaction(state["message"])

    if extracted is None:
        state["is_purchase"] = False
        return state

    state["is_purchase"] = True
    state["item"] = extracted["item"]
    state["amount"] = extracted["amount"]
    state["category"] = extracted["category"]
    state["currency"] = extracted["currency"]
    return state


def finalize_add_transaction_node(state: AgentState) -> AgentState:
    from db.models import get_budget, get_month_spent  # add to existing imports at top instead if you prefer

    tx_id = insert_transaction(
        user_id=state["user_id"],
        raw_text=state["message"],
        item=state["item"],
        amount=state["amount"],
        category=state["category"],
    )
    state["transaction_id"] = tx_id

    symbol = "₱" if state["currency"] == "PHP" else "$"
    tone = get_user_tone(state["user_id"])

    try:
        comment = generate_comment(
            state["item"], state["amount"], state["category"], state["currency"], tone
        )
    except Exception:
        comment = ""

    base = f"Logged: {state['item']} — {symbol}{state['amount']:.2f} ({state['category']})"
    response = f"{base}\n\n{comment}" if comment else base

    # Budget check
    limit = get_budget(state["user_id"], state["category"])
    if limit:
        spent = get_month_spent(state["user_id"], state["category"])
        pct = spent / limit
        if pct >= 1.0:
            response += f"\n\n⚠️ You're over your {state['category']} budget: ₱{spent:.2f} / ₱{limit:.2f}"
        elif pct >= 0.8:
            response += f"\n\n⚠️ Heads up — {pct*100:.0f}% of your {state['category']} budget used (₱{spent:.2f} / ₱{limit:.2f})"

    state["response"] = response
    return state


def classify_intent_node(state: AgentState) -> AgentState:
    """Only runs when try_extract_node found no purchase. Distinguishes
    a real spending question from idle chat/greetings."""
    state["intent"] = classify_intent(state["message"])
    return state


def query_transactions_node(state: AgentState) -> AgentState:
    from llm.query_extraction import extract_query_filters
    from db.models import query_transactions, get_budget, get_month_spent

    filters = extract_query_filters(state["message"])
    result = query_transactions(
        user_id=state["user_id"],
        category=filters["category"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
    )
    category_label = filters["category"] if filters["category"] else "all categories"

    if filters["query_type"] == "budget_remaining":
        if not filters["category"]:
            state["response"] = "Tell me which category — e.g. 'how much food budget is left'."
            return state
        limit = get_budget(state["user_id"], filters["category"])
        if not limit:
            state["response"] = f"You haven't set a budget for {filters['category']} yet."
            return state
        spent = get_month_spent(state["user_id"], filters["category"])
        remaining = limit - spent
        if remaining < 0:
            state["response"] = f"You're ₱{abs(remaining):.2f} over your {filters['category']} budget this month."
        else:
            state["response"] = f"₱{remaining:.2f} left in your {filters['category']} budget this month (₱{spent:.2f} of ₱{limit:.2f} used)."
        return state

    if filters["query_type"] == "list_transactions":
        if result["count"] == 0:
            state["response"] = "No transactions found for that."
            return state
        lines = [f"- {t['item']}: ₱{t['amount']:.2f} ({t['tx_timestamp'][:10]})" for t in result["transactions"]]
        state["response"] = f"Your {category_label} transactions:\n" + "\n".join(lines)
        return state

    # default: total_spent
    if result["count"] == 0:
        state["response"] = "No transactions found for that."
        return state
    state["response"] = (
        f"You spent ₱{result['total']:.2f} across {result['count']} transaction(s) in {category_label}."
    )
    return state


def fallback_reply_node(state: AgentState) -> AgentState:
    """Handles greetings/chat — anything that's neither a purchase nor a
    recognized spending query."""
    tone = get_user_tone(state["user_id"])
    try:
        state["response"] = generate_fallback_reply(state["message"], tone)
    except Exception:
        state["response"] = (
            "I didn't catch a purchase in that — try something like "
            "'fries $2' and I'll log it for you."
        )
    return state

def set_budget_node(state: AgentState) -> AgentState:
    from llm.budget_extraction import extract_budget
    from db.models import set_budget

    parsed = extract_budget(state["message"])
    if parsed is None:
        state["response"] = "I couldn't figure out the budget amount — try 'set food budget to 3000'."
        return state

    set_budget(state["user_id"], parsed["category"], parsed["limit_amount"])
    state["response"] = f"Budget set: {parsed['category']} — ₱{parsed['limit_amount']:.2f}/month"
    return state