from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import add_transaction_node

_graph = None


def get_graph():
    """Builds (once) and returns the compiled LangGraph.
    Phase 3 has exactly one node — more get added starting Phase 6."""
    global _graph
    if _graph is None:
        builder = StateGraph(AgentState)
        builder.add_node("add_transaction", add_transaction_node)
        builder.set_entry_point("add_transaction")
        builder.add_edge("add_transaction", END)
        _graph = builder.compile()
    return _graph


def run_agent(user_id: str, message: str) -> AgentState:
    """Entry point the rest of the app calls. Runs the graph on one message
    and returns the final state."""
    graph = get_graph()
    initial_state: AgentState = {
        "user_id": user_id,
        "message": message,
        "item": None,
        "amount": None,
        "category": None,
        "transaction_id": None,
        "response": None,
    }
    return graph.invoke(initial_state)