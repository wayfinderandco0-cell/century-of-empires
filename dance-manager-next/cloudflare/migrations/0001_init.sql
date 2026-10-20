PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS tickets (
 id TEXT PRIMARY KEY, channel TEXT NOT NULL, external_id TEXT UNIQUE,
 name TEXT NOT NULL DEFAULT '', email TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL DEFAULT '',
 studio TEXT NOT NULL DEFAULT '', visitor_type TEXT NOT NULL DEFAULT '',
 contact_method TEXT NOT NULL DEFAULT 'email', sms_consent INTEGER NOT NULL DEFAULT 0,
 call_consent INTEGER NOT NULL DEFAULT 0, marketing_opt_in INTEGER NOT NULL DEFAULT 0,
 summary TEXT NOT NULL DEFAULT '', transcript TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL DEFAULT 'needs_human' CHECK(status IN ('needs_human','claimed','resolved')),
 owner_alert_state TEXT NOT NULL DEFAULT 'not_attempted', ack_state TEXT NOT NULL DEFAULT 'not_attempted',
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS tickets_status_date ON tickets(status, created_at DESC);
CREATE INDEX IF NOT EXISTS tickets_email_date ON tickets(email, created_at DESC);
CREATE INDEX IF NOT EXISTS tickets_phone_date ON tickets(phone, created_at DESC);
CREATE TABLE IF NOT EXISTS ticket_messages (
 id TEXT PRIMARY KEY, ticket_id TEXT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
 direction TEXT NOT NULL CHECK(direction IN ('inbound','outbound','internal')),
 channel TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL,
 provider_id TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS messages_ticket_created ON ticket_messages(ticket_id, created_at);
CREATE TABLE IF NOT EXISTS deliveries (
 id TEXT PRIMARY KEY, ticket_id TEXT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
 kind TEXT NOT NULL, provider TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('accepted','failed','skipped')),
 reason TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS inbound_events (
 provider_id TEXT PRIMARY KEY, ticket_id TEXT, received_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rate_windows (
 bucket TEXT PRIMARY KEY, used INTEGER NOT NULL, expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sms_optouts (
 phone TEXT PRIMARY KEY, updated_at TEXT NOT NULL
);
