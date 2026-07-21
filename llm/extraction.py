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
Valid categories are: {', '.join(CATEGORIES)}.
If the category isn't obvious, use "Other".

Assume all amounts are in Philippine Pesos (PHP) unless the user explicitly
states another currency (e.g. "$5 USD", "10 dollars"). Do not treat "$" as
a signal for US dollars by default — in this app, a bare number or a "$"
symbol both default to PHP pesos.

IMPORTANT: Only call the extract_transaction tool if the message clearly
describes an actual purchase with a real amount greater than zero. If the
message is a greeting, question, or doesn't contain a purchase, do NOT call
the tool — just respond normally with no tool call.
Also return a snarky or humurous comment roasting the purchase of the user but keep it short."""


def extract_transaction(message: str) -> dict | None:
    """Calls Groq with tool-calling to extract {item, amount, category} from a raw message.
    Returns None if the message doesn't appear to describe a purchase."""
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        tools=[EXTRACT_TOOL],
        tool_choice="auto",
        reasoning_effort="low",
    )

    choice = response.choices[0]
    tool_calls = choice.message.tool_calls

    if not tool_calls:
        return None  # message wasn't a purchase — caller decides how to respond

    args = json.loads(tool_calls[0].function.arguments)
    amount = float(args["amount"])

    # Defensive check: never trust the model blindly. If it called the tool
    # but the amount is nonsensical, treat it as "not a real purchase"
    # rather than letting bad data reach the database layer.
    if amount <= 0:
        return None

    return {
        "item": args["item"],
        "amount": amount,
        "category": args["category"],
        "currency": args.get("currency", "PHP"),
    }