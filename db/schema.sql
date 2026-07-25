CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    tone_pref TEXT DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    item TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    category TEXT NOT NULL,
    tx_timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,
    limit_amount NUMERIC(12,2) NOT NULL,
    period TEXT NOT NULL DEFAULT 'monthly',
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    UNIQUE(user_id, category, period)
);


CREATE TABLE IF NOT EXISTS interaction_log (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    raw_message TEXT NOT NULL,
    intent TEXT,
    extracted_json JSONB,
    response TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_transactions_user_id
ON transactions(user_id);


CREATE INDEX IF NOT EXISTS idx_budgets_user_id
ON budgets(user_id);


CREATE INDEX IF NOT EXISTS idx_interaction_log_user_id
ON interaction_log(user_id);