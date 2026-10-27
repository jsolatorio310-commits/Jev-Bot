CREATE TABLE ledger_events (
  event_id UUID PRIMARY KEY,
  event_key TEXT NOT NULL UNIQUE,
  event_type TEXT NOT NULL CHECK (event_type IN ('balance', 'position', 'order', 'fill')),
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE balances (
  asset TEXT PRIMARY KEY,
  amount NUMERIC NOT NULL
);

CREATE TABLE positions (
  symbol TEXT PRIMARY KEY,
  quantity NUMERIC NOT NULL,
  average_price NUMERIC NOT NULL
);

