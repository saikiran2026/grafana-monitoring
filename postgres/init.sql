-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create metrics table
CREATE TABLE IF NOT EXISTS metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL,
    value DOUBLE PRECISION,
    tags JSONB
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('metrics', 'time', if_not_exists => TRUE);

-- Create index on metric_name for faster queries
CREATE INDEX IF NOT EXISTS idx_metric_name ON metrics (metric_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_tags ON metrics USING GIN (tags);

-- Create sample data views
CREATE TABLE IF NOT EXISTS server_metrics (
    time TIMESTAMPTZ NOT NULL,
    server_name TEXT NOT NULL,
    cpu_usage DOUBLE PRECISION,
    memory_usage DOUBLE PRECISION,
    disk_usage DOUBLE PRECISION,
    network_in DOUBLE PRECISION,
    network_out DOUBLE PRECISION
);

SELECT create_hypertable('server_metrics', 'time', if_not_exists => TRUE);

-- Create application metrics table
CREATE TABLE IF NOT EXISTS application_metrics (
    time TIMESTAMPTZ NOT NULL,
    app_name TEXT NOT NULL,
    request_count INTEGER,
    error_count INTEGER,
    response_time DOUBLE PRECISION,
    active_users INTEGER
);

SELECT create_hypertable('application_metrics', 'time', if_not_exists => TRUE);

-- Create business metrics table
CREATE TABLE IF NOT EXISTS business_metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_type TEXT NOT NULL,
    revenue DOUBLE PRECISION,
    transactions INTEGER,
    conversion_rate DOUBLE PRECISION
);

SELECT create_hypertable('business_metrics', 'time', if_not_exists => TRUE);

