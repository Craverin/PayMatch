CREATE TABLE sync_runs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status VARCHAR(9) NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'succeeded', 'failed')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    orders_imported INTEGER NOT NULL DEFAULT 0 CHECK (orders_imported >= 0),
    payments_imported INTEGER NOT NULL DEFAULT 0 CHECK (payments_imported >= 0),
    error_message TEXT
);

CREATE UNIQUE INDEX uq_sync_runs_single_running
ON sync_runs (status)
WHERE status = 'running';

CREATE TABLE orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE CHECK (trim(external_id) <> ''),
    amount_minor BIGINT NOT NULL CHECK (amount_minor >= 0),
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD')),
    order_status VARCHAR(9) NOT NULL CHECK (order_status IN ('open', 'cancelled')),
    payment_status VARCHAR(6) NOT NULL CHECK (payment_status IN ('unpaid', 'paid')),
    external_created_at TIMESTAMPTZ NOT NULL,
    external_updated_at TIMESTAMPTZ NOT NULL,
    last_sync_run_id BIGINT NOT NULL REFERENCES sync_runs(id)
);

CREATE TABLE payments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE CHECK (trim(external_id) <> ''),
    external_order_id TEXT CHECK (external_order_id IS NULL OR trim(external_order_id) <> ''),
    amount_minor BIGINT NOT NULL CHECK (amount_minor >= 0),
    amount_received_minor BIGINT NOT NULL CHECK (amount_received_minor >= 0),
    currency TEXT NOT NULL CHECK (currency IN ('EUR', 'USD')),
    provider_status TEXT NOT NULL,
    capture_method TEXT NOT NULL,
    external_created_at TIMESTAMPTZ NOT NULL,
    last_changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_sync_run_id BIGINT NOT NULL REFERENCES sync_runs(id),

    CONSTRAINT ck_payments_provider_status CHECK (provider_status IN (
        'requires_payment_method', 'requires_confirmation', 'requires_action',
        'processing', 'requires_capture', 'canceled', 'succeeded'
    )),
    CONSTRAINT ck_payments_capture_method CHECK (capture_method IN (
        'automatic', 'automatic_async', 'manual'
    ))
);

CREATE TABLE issues (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id),
    payment_id BIGINT REFERENCES payments(id),
    code TEXT NOT NULL CHECK (trim(code) <> ''),
    status VARCHAR(8) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'ignored')),
    details JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,

    CONSTRAINT ck_issues_has_subject CHECK (order_id IS NOT NULL OR payment_id IS NOT NULL),
    CONSTRAINT uq_issues_order_payment_code UNIQUE NULLS NOT DISTINCT (order_id, payment_id, code),
    CONSTRAINT ck_issues_resolved_at CHECK (
        (status = 'resolved' AND resolved_at IS NOT NULL)
        OR (status <> 'resolved' AND resolved_at IS NULL)
    )
);
