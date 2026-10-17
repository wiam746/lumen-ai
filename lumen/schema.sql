-- Lumen AI schema (SQLite). Timestamps are UTC, format 'YYYY-MM-DD HH:MM:SS'.
-- Prompts and responses are stored ENCRYPTED (Fernet) in *_enc columns.

CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash       TEXT    NOT NULL,
    role                TEXT    NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_blocked          INTEGER NOT NULL DEFAULT 0,
    blocked_reason      TEXT,
    external_ai_optout  INTEGER NOT NULL DEFAULT 0,
    policy_version      TEXT    NOT NULL,
    policy_accepted_at  TEXT    NOT NULL,
    created_at          TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at       TEXT
);

CREATE TABLE IF NOT EXISTS requests (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    prompt_enc         TEXT    NOT NULL,
    response_enc       TEXT    NOT NULL,
    provider           TEXT    NOT NULL,
    model              TEXT    NOT NULL,
    external_transfer  INTEGER NOT NULL DEFAULT 0,
    is_flagged         INTEGER NOT NULL DEFAULT 0,
    flag_reason        TEXT    NOT NULL DEFAULT '',
    review_status      TEXT    NOT NULL DEFAULT 'none'
                       CHECK (review_status IN ('none', 'pending', 'validated', 'warned', 'blocked')),
    review_note        TEXT,
    reviewed_by        INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at        TEXT,
    created_at         TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_requests_user    ON requests(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_requests_review  ON requests(review_status);
CREATE INDEX IF NOT EXISTS idx_requests_created ON requests(created_at);

CREATE TABLE IF NOT EXISTS warnings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_id  INTEGER,
    reason      TEXT    NOT NULL,
    created_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Contestation procedure (GDPR Art. 22(3), Art. 21): a human always decides.
CREATE TABLE IF NOT EXISTS contests (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_id    INTEGER,
    kind          TEXT    NOT NULL CHECK (kind IN ('ai_output', 'moderation', 'other')),
    message       TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'accepted', 'rejected')),
    decision_note TEXT,
    decided_by    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    decided_at    TEXT,
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_contests_status ON contests(status);

-- Brute-force throttling. Keys are HMAC digests: no raw IP or username is stored.
CREATE TABLE IF NOT EXISTS login_attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash    TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_login_attempts ON login_attempts(key_hash, created_at);

-- Tamper-evident audit trail: each event embeds the hash of the previous one.
CREATE TABLE IF NOT EXISTS audit_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT NOT NULL,
    actor       TEXT NOT NULL,
    action      TEXT NOT NULL,
    target      TEXT NOT NULL DEFAULT '',
    detail      TEXT NOT NULL DEFAULT '{}',
    ip_masked   TEXT NOT NULL DEFAULT '-',
    prev_hash   TEXT NOT NULL UNIQUE,
    hash        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
