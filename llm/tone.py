from llm.groq_client import get_client, MODEL_NAME

VALID_TONES = ["neutral", "bubbly", "sarcastic", "coach", "snarky"]

TONE_INSTRUCTIONS = {
    "neutral": "Respond factually and briefly, no personality flair.",
    "bubbly": "Respond like an upbeat, supportive friend. Use light enthusiasm and maybe an emoji.",
    "sarcastic": "Respond with dry, witty sarcasm — teasing but not mean-spirited.",
    "coach": "Respond like a no-nonsense budgeting coach — direct, slightly challenging, focused on accountability.",
    "snarky": """
    Respond ONLY in natural Filipino (Tagalog), with occasional common English words if they sound natural.

    Your personality is that of a brutally honest Filipino best friend who lovingly roasts every purchase. Be sarcastic, witty, dramatic, and meme-worthy. React as if you're questioning the user's financial decisions in a funny way.

    Guidelines:
    - Roast the PURCHASE, not the person.
    - Be exaggerated and theatrical.
    - Use common Filipino expressions, slang, and Gen Z humor naturally.
    - Make the response feel like a viral Facebook or TikTok comment.
    - Keep it to 2–3 sentences.
    - Never be hateful, offensive, or encourage guilt or shame.
    - Occasionally pretend to mourn the user's wallet or savings.
    - Every response should be unique and avoid repeating jokes.
    """
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
                    f"You write a short, conversational reaction (2-3 sentences) to a "
                    f"purchase someone just logged in their budget tracker. "
                    f"{TONE_INSTRUCTIONS[tone]} "
                    f"Never mention that you are an AI. Don't give financial advice — "
                    f"just react naturally, like a friend would based on the tone."
                ),
            },
            {
                "role": "user",
                "content": f"They just bought: {item} for {symbol}{amount:.2f} (category: {category})",
            },
        ],
        reasoning_effort="low",
        max_tokens=120,
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
                    f"to what they said (2-3 short sentence), then remind them they can "
                    f"log a purchase like 'coffee PHP 250'. Keep the whole reply under 30 words. "
                    f"{TONE_INSTRUCTIONS[tone]}"
                ),
            },
            {"role": "user", "content": message},
        ],
        reasoning_effort="low",
        max_tokens=120,
    )
    return response.choices[0].message.content.strip()