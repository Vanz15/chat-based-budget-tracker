import json
from llm.groq_client import get_client, MODEL_NAME

# Fixed category list — keeps categorization consistent instead of letting
# the model invent new categories freely (see earlier discussion on category drift).
CATEGORIES = [
    "Food", "Transport", "Bills", "Shopping",
    "Entertainment", "Health", "Personal Care", "Other",
]

EXTRACT_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_transaction",
        "description": "Extract a purchase's item, amount, and category from a user's message.",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {
                    "type": "string",
                    "description": "Short description of what was purchased, e.g. 'fries'",
                },
                "amount": {
                    "type": "number",
                    "description": "The numeric cost of the purchase, no currency symbol",
                },
                "category": {
                    "type": "string",
                    "enum": CATEGORIES,
                    "description": "Best-fit category for this purchase",
                },
            },
            "required": ["item", "amount", "category"],
        },
    },
}

SYSTEM_PROMPT = f"""You extract purchase details from short user messages.
Always call the extract_transaction tool with your best-guess values.
Valid categories are: {', '.join(CATEGORIES)}.
If the category isn't obvious, use "Other"."""


def extract_transaction(message: str) -> dict:
    """Calls Groq with tool-calling to extract {item, amount, category} from a raw message.
    Raises RuntimeError if the model doesn't return a usable tool call."""
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        tools=[EXTRACT_TOOL],
        tool_choice={"type": "function", "function": {"name": "extract_transaction"}},
        reasoning_effort="low",  # keep extraction fast, no need for deep reasoning
    )

    choice = response.choices[0]
    tool_calls = choice.message.tool_calls

    if not tool_calls:
        raise RuntimeError(f"Model did not return a tool call. Raw response: {choice.message.content}")

    args = json.loads(tool_calls[0].function.arguments)
    return {
        "item": args["item"],
        "amount": float(args["amount"]),
        "category": args["category"],
    }