-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ── Transactions table ────────────────────────────────────────────────────
-- Note: TimescaleDB requires partition column (timestamp) in primary key
CREATE TABLE IF NOT EXISTS transactions (
    txn_id              UUID NOT NULL DEFAULT gen_random_uuid(),
    sender_vpa_masked   TEXT NOT NULL,
    receiver_vpa_masked TEXT NOT NULL,
    amount              DECIMAL(15,2) NOT NULL,
    timestamp           TIMESTAMPTZ NOT NULL,
    device_id_hash      TEXT,
    ip_hash             TEXT,
    gps_lat             FLOAT,
    gps_lng             FLOAT,
    merchant_code       TEXT,
    upi_app             TEXT,
    raw_payload         JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (txn_id, timestamp)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('transactions', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ── Fraud decisions table ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fraud_decisions (
    decision_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    txn_id              UUID,
    composite_score     FLOAT NOT NULL,
    ml_score            FLOAT,
    graph_score         FLOAT,
    anomaly_score       FLOAT,
    decision            VARCHAR(10) CHECK (decision IN ('SAFE','REVIEW','BLOCK')),
    model_version       TEXT,
    shap_values         JSONB,
    decided_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ── Fraud cases table ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fraud_cases (
    case_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    txn_id              UUID NOT NULL,
    risk_score          FLOAT,
    status              VARCHAR(20) DEFAULT 'OPEN',
    assigned_analyst    TEXT,
    sla_deadline        TIMESTAMPTZ,
    disposition         VARCHAR(20),
    disposition_notes   TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    closed_at           TIMESTAMPTZ
);

-- ── Case labels table ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_labels (
    label_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id             UUID REFERENCES fraud_cases(case_id),
    txn_id              UUID,
    label               VARCHAR(20) CHECK (label IN ('TRUE_FRAUD','FALSE_POSITIVE','INCONCLUSIVE')),
    analyst_id          TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ── Analyst actions table ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analyst_actions (
    action_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analyst_id          TEXT NOT NULL,
    case_id             UUID REFERENCES fraud_cases(case_id),
    action_type         TEXT,
    details             JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_transactions_sender
    ON transactions(sender_vpa_masked, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_decisions_txn
    ON fraud_decisions(txn_id);

CREATE INDEX IF NOT EXISTS idx_cases_status_analyst
    ON fraud_cases(status, assigned_analyst);

CREATE INDEX IF NOT EXISTS idx_cases_sla
    ON fraud_cases(sla_deadline);

CREATE INDEX IF NOT EXISTS idx_labels_case
    ON case_labels(case_id);