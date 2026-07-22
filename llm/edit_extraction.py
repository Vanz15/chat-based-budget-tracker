import json
from llm.groq_client import get_client, MODEL_NAME
from llm.extraction import CATEGORIES

EDIT_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_edit",
        "description": "Extract what the user wants to change about a past transaction.",
        "parameters": {
            "type": "object",
            "properties": {
                "item_hint": {
                    "type": "string",
                    "description": "Keyword identifying which transaction, if mentioned (e.g. 'coffee', 'yesterday's lunch'). Empty string if not specified — assume most recent.",
                },
                "new_amount": {"type": "number", "description": "New amount, if being changed. 0 if not changing amount."},
                "new_category": {"type": "string", "enum": CATEGORIES + ["none"], "description": "New category, if being changed. 'none' if not changing category."},
            },
            "required": ["item_hint", "new_amount", "new_category"],
        },
    },
}

SYSTEM_PROMPT = """Extract what the user wants to change about a logged purchase.
Examples: "actually that was 30 not 3" -> new_amount=30, no item hint (means most recent).
"change yesterday's coffee to 150" -> item_hint="coffee", new_amount=150."""


def extract_edit(message: str):
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message}],
        tools=[EDIT_TOOL],
        tool_choice={"type": "function", "function": {"name": "extract_edit"}},
        reasoning_effort="low",
    )
    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls:
        return None
    args = json.loads(tool_calls[0].function.arguments)
    return {
        "item_hint": args.get("item_hint") or None,
        "new_amount": args["new_amount"] if args["new_amount"] > 0 else None,
        "new_category": args["new_category"] if args["new_category"] != "none" else None,
    }