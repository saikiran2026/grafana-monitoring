-- Synthetic Monitoring Tables for uptime/availability monitoring

-- Probes table (monitoring locations)
CREATE TABLE IF NOT EXISTS probes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    region TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    online BOOLEAN DEFAULT TRUE
);

-- Insert probe locations
INSERT INTO probes (name, region, latitude, longitude) VALUES
    ('us-east-1', 'N. Virginia', 37.4316, -78.6569),
    ('us-west-1', 'N. California', 37.3541, -121.9552),
    ('eu-west-1', 'Ireland', 53.3498, -6.2603),
    ('eu-central-1', 'Frankfurt', 50.1109, 8.6821),
    ('ap-southeast-1', 'Singapore', 1.3521, 103.8198),
    ('ap-northeast-1', 'Tokyo', 35.6762, 139.6503)
ON CONFLICT (name) DO NOTHING;

-- HTTP checks table
CREATE TABLE IF NOT EXISTS http_checks (
    time TIMESTAMPTZ NOT NULL,
    check_name TEXT NOT NULL,
    target_url TEXT NOT NULL,
    probe_name TEXT NOT NULL,
    status_code INTEGER,
    response_time_ms DOUBLE PRECISION,
    success BOOLEAN,
    ssl_expiry_days INTEGER,
    dns_time_ms DOUBLE PRECISION,
    connect_time_ms DOUBLE PRECISION,
    error_message TEXT
);

SELECT create_hypertable('http_checks', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_http_checks_name ON http_checks (check_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_http_checks_probe ON http_checks (probe_name, time DESC);

-- Ping/ICMP checks table
CREATE TABLE IF NOT EXISTS ping_checks (
    time TIMESTAMPTZ NOT NULL,
    check_name TEXT NOT NULL,
    target_host TEXT NOT NULL,
    probe_name TEXT NOT NULL,
    latency_ms DOUBLE PRECISION,
    packet_loss DOUBLE PRECISION,
    success BOOLEAN,
    error_message TEXT
);

SELECT create_hypertable('ping_checks', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_ping_checks_name ON ping_checks (check_name, time DESC);

-- DNS checks table
CREATE TABLE IF NOT EXISTS dns_checks (
    time TIMESTAMPTZ NOT NULL,
    check_name TEXT NOT NULL,
    target_domain TEXT NOT NULL,
    probe_name TEXT NOT NULL,
    resolution_time_ms DOUBLE PRECISION,
    success BOOLEAN,
    resolved_ips TEXT[],
    error_message TEXT
);

SELECT create_hypertable('dns_checks', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_dns_checks_name ON dns_checks (check_name, time DESC);

-- TCP checks table
CREATE TABLE IF NOT EXISTS tcp_checks (
    time TIMESTAMPTZ NOT NULL,
    check_name TEXT NOT NULL,
    target_host TEXT NOT NULL,
    target_port INTEGER NOT NULL,
    probe_name TEXT NOT NULL,
    connect_time_ms DOUBLE PRECISION,
    success BOOLEAN,
    error_message TEXT
);

SELECT create_hypertable('tcp_checks', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_tcp_checks_name ON tcp_checks (check_name, time DESC);

-- Uptime summary view (for dashboard)
CREATE OR REPLACE VIEW uptime_summary AS
SELECT 
    check_name,
    COUNT(*) as total_checks,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_checks,
    ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as uptime_percentage,
    AVG(response_time_ms) as avg_response_time,
    MAX(response_time_ms) as max_response_time,
    MIN(CASE WHEN success THEN response_time_ms END) as min_response_time
FROM http_checks
WHERE time > NOW() - INTERVAL '24 hours'
GROUP BY check_name;

