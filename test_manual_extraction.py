from llm.extraction import extract_transaction

test_messages = [
    "fries $2",
    "i bought fries for $2",
    "bought a phone case for 350",
    "coffee 150",
    "paid 1200 for electricity bill",
    "grabbed a haircut, 250 pesos",
]

for msg in test_messages:
    result = extract_transaction(msg)
    print(f"'{msg}' -> {result}")    