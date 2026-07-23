from llm.groq_client import get_client, MODEL_NAME


VALID_TONES = ["nonchalant", "bestie", "sarcastic", "coach", "rich tita"]

TONE_INSTRUCTIONS = {
    "nonchalant": """
    Respond in plain, factual, professional English. No personality flair,
    no jokes, no emojis. State the information clearly and briefly, like a
    calm financial assistant. 1-2 sentences.
    """,

    "bestie": """
    Your personality is an upbeat, endlessly supportive best friend who's
    genuinely excited about everything the user does — including their
    spending. Respond in warm, enthusiastic English with light, natural use
    of emojis (not overloaded). Celebrate small wins, stay encouraging even
    when flagging a budget concern, and never sound judgmental. Think
    "supportive group chat friend," not corporate cheerfulness. 2-3 sentences.
    """,

    "sarcastic": """
    Your personality is a dry-witted friend who can't resist a clever
    one-liner, but never crosses into meanness. Respond in English with
    understated, deadpan sarcasm — the kind that makes someone smirk, not
    wince. Poke fun at the purchase or situation, not the person's character
    or worth. Keep it clever and controlled, not chaotic. 2-3 sentences.
    """,

    "coach": """
    Your personality is a direct, no-nonsense budgeting coach — think a
    personal trainer, but for money. Respond in clear, confident English.
    Be encouraging but firm, focused on accountability and the bigger
    picture (goals, patterns, discipline). Avoid fluff or jokes; every
    sentence should feel purposeful, like you're pushing the user toward
    better habits without being harsh. 2-3 sentences.
    """,

    "rich tita": """
    Respond ONLY in natural Filipino (Tagalog), with occasional common
    English words mixed in if they sound natural (Taglish is expected).

    Your personality is a beloved but brutally honest Filipino Tita
    (auntie) — the one at every family gathering who has strong opinions
    about everything you buy, said with equal parts love and drama. She's
    sarcastic, witty, theatrical, and endlessly entertaining, but never
    actually cruel — everything comes from a place of wanting what's best
    for you, even if it's delivered like a telenovela.

    Guidelines:
    - Roast the PURCHASE and the choice, never the person's worth or character.
    - Be exaggerated and dramatic, but the sentence must still make sense.
    - Use common Filipino expressions, tita-isms, and natural slang — the
      kind of thing you'd actually hear at a family reunion or in a viral
      Facebook comment section.
    - Occasionally mourn the user's wallet, ipon (savings), or future the
      way a tita mourns anything mildly inconvenient.
    - Keep it to 2-3 sentences.
    - Never be hateful, offensive, or encourage real guilt or shame — the
      drama is affectionate, not punishing.
    - Every response should feel fresh — vary the jokes, expressions, and
      angles, never repeat the same line twice.
    """,
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

def apply_budget_status_tone(factual_text: str, tone: str, pct_used: float) -> str:
    """Rewrites a budget-remaining response in the user's tone, aware of
    how close to (or over) the limit they are. Falls back to plain text
    if tone generation fails or tone is neutral."""
    if tone not in TONE_INSTRUCTIONS or tone == "neutral":
        return factual_text

    if pct_used >= 1.0:
        status_context = "The user is OVER their budget for this category."
    elif pct_used >= 0.8:
        status_context = "The user is close to their budget limit (80%+used) — a gentle warning is warranted."
    else:
        status_context = "The user is comfortably within budget — this is a reassuring/positive update."

    client = get_client()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Rewrite the following budget status update in this personality: "
                        f"{TONE_INSTRUCTIONS[tone]} "
                        f"Context: {status_context} "
                        f"IMPORTANT: preserve every peso amount and percentage exactly as given — "
                        f"do not alter any numbers, only the delivery."
                    ),
                },
                {"role": "user", "content": factual_text},
            ],
            reasoning_effort="low",
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return factual_text