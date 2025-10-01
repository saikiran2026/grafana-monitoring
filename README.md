# Grafana Synthetic Data Demo

A complete local Grafana setup with synthetic data generation, similar to [Grafana Play](https://play.grafana.org). This project provides a fully functional Grafana instance with pre-configured dashboards, real-time synthetic metrics, and multiple data sources.

## 🚀 Features

- **Grafana** with pre-configured dashboards
- **Prometheus** for real-time metrics
- **PostgreSQL with TimescaleDB** for time-series data storage
- **Synthetic Data Generator** that creates realistic:
  - Server metrics (CPU, memory, disk, network)
  - Application metrics (requests, errors, response times, active users)
  - Business metrics (revenue, transactions, conversion rates)
- **24 hours of historical data** on startup
- **Real-time data generation** every 15 seconds
- **Beautiful pre-built dashboards** showcasing various visualization types

## 📋 Prerequisites

- [Docker](https://www.docker.com/get-started) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)

## 🏃 Quick Start

### 1. Start the Stack

```bash
docker-compose up -d
```

This will start:
- Grafana on http://localhost:3000
- Prometheus on http://localhost:9090
- PostgreSQL on localhost:5432
- Prometheus Pushgateway on http://localhost:9091

### 2. Access Grafana

1. Open your browser to http://localhost:3000
2. Login credentials:
   - **Username**: `admin`
   - **Password**: `admin`
3. Navigate to **Dashboards** → **Getting Started with Grafana - Synthetic Data**

### 3. View the Data

The data generator will:
- Generate 24 hours of historical data on first startup (takes ~2 minutes)
- Continue generating real-time data every 15 seconds
- Populate both Prometheus and PostgreSQL

## 📊 What's Included

### Data Sources

1. **Prometheus** (Default)
   - Real-time metrics
   - 15-second scrape interval
   - System and application metrics

2. **PostgreSQL (TimescaleDB)**
   - Time-series optimized
   - Historical data storage
   - Complex query capabilities

### Dashboards

#### Getting Started Dashboard

Includes panels for:
- **CPU Usage by Server** - Time series graph showing CPU utilization across all servers
- **Memory Usage by Server** - Memory consumption trends
- **Total HTTP Requests** - Gauge showing current request volume
- **Average Response Time** - Application performance metrics
- **Active Users** - Real-time user count
- **Current Revenue** - Business metrics
- **Requests per Application** - PostgreSQL-based time series
- **Response Time per Application** - Performance by service

### Synthetic Data

The data generator creates realistic metrics for:

**Servers**:
- `web-server-01`, `web-server-02`
- `api-server-01`, `api-server-02`
- `db-server-01`

**Applications**:
- `frontend`
- `backend-api`
- `payment-service`
- `auth-service`
- `notification-service`

**Patterns**:
- Traffic increases during "business hours" (9 AM - 5 PM)
- Random variations to simulate real-world behavior
- Occasional spikes and anomalies

## 🛠️ Management Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f data-generator
docker-compose logs -f grafana
```

### Restart Data Generator
```bash
docker-compose restart data-generator
```

### Reset Everything (Delete All Data)
```bash
docker-compose down -v
docker-compose up -d
```

## 📁 Project Structure

```
grafana-synthentic/
├── docker-compose.yml              # Main orchestration file
├── data-generator/
│   ├── Dockerfile                  # Data generator container
│   ├── requirements.txt            # Python dependencies
│   └── generate_data.py           # Synthetic data generation script
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/           # Pre-configured data sources
│   │   │   └── datasources.yml
│   │   └── dashboards/            # Dashboard provisioning
│   │       └── dashboards.yml
│   └── dashboards/
│       └── getting-started.json   # Main demo dashboard
├── prometheus/
│   └── prometheus.yml             # Prometheus configuration
└── postgres/
    └── init.sql                   # Database initialization
```

## 🎨 Customization

### Add More Servers or Applications

Edit `data-generator/generate_data.py`:

```python
SERVERS = ['web-server-01', 'web-server-02', 'your-server']
APPLICATIONS = ['frontend', 'backend-api', 'your-app']
```

### Adjust Data Generation Frequency

In `data-generator/generate_data.py`, modify:

```python
time.sleep(15)  # Change to desired interval in seconds
```

### Create New Dashboards

1. Log into Grafana
2. Create your dashboard
3. Export as JSON
4. Save to `grafana/dashboards/`
5. Restart Grafana: `docker-compose restart grafana`

### Change Historical Data Period

In `data-generator/generate_data.py`:

```python
self.generate_historical_data(hours=24)  # Change hours value
```

## 🔍 Querying Data

### Prometheus Queries

Example PromQL queries:

```promql
# Average CPU usage
avg(system_cpu_usage)

# CPU usage by server
system_cpu_usage{server="web-server-01"}

# Total requests
sum(http_requests_total)

# Error rate
sum(http_requests_total{status="500"}) / sum(http_requests_total)
```

### PostgreSQL Queries

Access the database:

```bash
docker-compose exec postgres psql -U grafana -d synthetic_data
```

Example queries:

```sql
-- Average CPU by server (last hour)
SELECT 
    server_name,
    AVG(cpu_usage) as avg_cpu
FROM server_metrics
WHERE time > NOW() - INTERVAL '1 hour'
GROUP BY server_name;

-- Application performance
SELECT 
    app_name,
    AVG(response_time) as avg_response,
    SUM(request_count) as total_requests
FROM application_metrics
WHERE time > NOW() - INTERVAL '1 hour'
GROUP BY app_name;
```

## 🐛 Troubleshooting

### Data Not Showing

1. Check if data generator is running:
   ```bash
   docker-compose ps data-generator
   ```

2. View data generator logs:
   ```bash
   docker-compose logs data-generator
   ```

3. Verify database connection:
   ```bash
   docker-compose exec postgres psql -U grafana -d synthetic_data -c "SELECT COUNT(*) FROM server_metrics;"
   ```

### Grafana Not Loading

1. Check Grafana logs:
   ```bash
   docker-compose logs grafana
   ```

2. Ensure port 3000 is not in use:
   ```bash
   lsof -i :3000
   ```

3. Restart Grafana:
   ```bash
   docker-compose restart grafana
   ```

### Prometheus Data Issues

1. Check Prometheus targets: http://localhost:9090/targets
2. Verify pushgateway is accessible: http://localhost:9091
3. Check Prometheus logs:
   ```bash
   docker-compose logs prometheus
   ```

## 📝 Notes

- The data generator creates realistic patterns but is entirely synthetic
- Historical data generation can take 2-3 minutes on first startup
- Data is persisted in Docker volumes; use `docker-compose down -v` to reset
- Grafana dashboards are provisioned automatically on startup
- You can modify dashboards in the UI; changes won't persist after restart unless exported

## 🤝 Contributing

Feel free to:
- Add more synthetic data types
- Create additional dashboards
- Improve data generation algorithms
- Add more data sources (InfluxDB, Elasticsearch, etc.)

## 📄 License

This project is open source and available for learning and demonstration purposes.

## 🔗 Useful Links

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Grafana Play (Official Demo)](https://play.grafana.org/)

---

**Enjoy exploring Grafana with realistic synthetic data! 📊✨**

