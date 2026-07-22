import json
from datetime import date, timedelta
from llm.groq_client import get_client, MODEL_NAME
from llm.extraction import CATEGORIES

QUERY_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_query_filters",
        "description": "Extract filters from a natural language spending question.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": CATEGORIES + ["all"],
                    "description": "Category to filter by, or 'all' if not specified",
                },
                "period": {
                    "type": "string",
                    "enum": ["today", "this_week", "this_month", "all_time"],
                    "description": "Time range implied by the question. Default to 'all_time' if unclear.",
                },
                "query_type": {
                    "type": "string",
                    "enum": ["total_spent", "budget_remaining", "list_transactions"],
                    "description": (
                        "'total_spent' for questions like 'how much did I spend'. "
                        "'budget_remaining' for questions like 'how much budget is left' or 'am I over budget'. "
                        "'list_transactions' for questions like 'show me my transactions' or 'what did I buy'."
                    ),
                },
            },
            "required": ["category", "period", "query_type"],
        },
    },
}

SYSTEM_PROMPT = """You extract filters from a spending question so it can be
queried against a database. Always call extract_query_filters.
If no category is mentioned, use "all". If no time period is mentioned, use "all_time"."""


def extract_query_filters(message: str) -> dict:
    """Returns {category, start_date, end_date} ready to use in a DB query."""
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        tools=[QUERY_TOOL],
        tool_choice={"type": "function", "function": {"name": "extract_query_filters"}},
        reasoning_effort="low",
    )
    args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

    category = args.get("category", "all")
    period = args.get("period", "all_time")

    today = date.today()
    if period == "today":
        start_date = today.isoformat()
    elif period == "this_week":
        start_date = (today - timedelta(days=today.weekday())).isoformat()
    elif period == "this_month":
        start_date = today.replace(day=1).isoformat()
    else:
        start_date = None

    return {
        "category": None if category == "all" else category,
        "start_date": start_date,
        "end_date": today.isoformat() if start_date else None,
        "query_type": args.get("query_type", "total_spent"),
    }