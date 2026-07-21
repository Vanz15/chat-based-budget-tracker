from llm.groq_client import get_client, MODEL_NAME

VALID_TONES = ["neutral", "bubbly", "sarcastic", "coach", "snarky"]

TONE_INSTRUCTIONS = {
    "neutral": "Respond factually and briefly, no personality flair.",
    "bubbly": "Respond like an upbeat, supportive friend. Use light enthusiasm and maybe an emoji.",
    "sarcastic": "Respond with dry, witty sarcasm — teasing but not mean-spirited.",
    "coach": "Respond like a no-nonsense budgeting coach — direct, slightly challenging, focused on accountability.",
    "snarky": "Respond with a touch of snark — playful but not malicious. make it humurous and witty."
}


def generate_comment(item: str, amount: float, category: str, currency: str, tone: str) -> str:
    """Generates a short (1 sentence) tone-matched reaction to a logged purchase."""
    if tone not in TONE_INSTRUCTIONS:
        tone = "neutral"

    symbol = "₱" if currency == "PHP" else "$"

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You write a single short reaction sentence (max 20 words) to a "
                    f"purchase someone just logged in their budget tracker. "
                    f"{TONE_INSTRUCTIONS[tone]} "
                    f"Never mention that you are an AI. Never give financial advice paragraphs — "
                    f"just one reactive sentence."
                ),
            },
            {
                "role": "user",
                "content": f"They just bought: {item} for {symbol}{amount:.2f} (category: {category})",
            },
        ],
        reasoning_effort="low",
        max_tokens=60,
    )
    return response.choices[0].message.content.strip()

def generate_fallback_reply(message: str, tone: str) -> str:
    """Generates a short, polite conversational reply for non-purchase
    messages (greetings, questions, etc.), then reminds the user what
    the app is for."""
    if tone not in TONE_INSTRUCTIONS:
        tone = "neutral"

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a budget tracker chat assistant. The user just sent a "
                    f"message that isn't a purchase to log. Reply briefly and politely "
                    f"to what they said (1-2 short sentence), then remind them they can "
                    f"log a purchase like 'coffee PHP 250'. Keep the whole reply under 30 words. "
                    f"{TONE_INSTRUCTIONS[tone]}"
                ),
            },
            {"role": "user", "content": message},
        ],
        reasoning_effort="low",
        max_tokens=60,
    )
    return response.choices[0].message.content.strip()