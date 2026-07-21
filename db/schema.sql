-- Minimal schema for prototype v1
-- Keep it simple: just transactions for now. Budgets/users come later.

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    tone_pref TEXT DEFAULT 'neutral',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    item TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    tx_timestamp TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);