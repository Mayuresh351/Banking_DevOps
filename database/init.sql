CREATE TABLE users_account_info (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions_info (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_account_info(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('deposit', 'withdraw')),
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
