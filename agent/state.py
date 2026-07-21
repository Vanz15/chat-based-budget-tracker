from typing import TypedDict, Optional


class AgentState(TypedDict):
    """Shared state passed between LangGraph nodes.
    Grows over future phases (intent, tone, query filters, etc.) —
    kept minimal for Phase 3."""
    user_id: str
    message: str                    # raw input from the user
    item: Optional[str]
    amount: Optional[float]
    category: Optional[str]
    transaction_id: Optional[int]   # set once inserted into DB
    response: Optional[str]         # what gets shown back to the user