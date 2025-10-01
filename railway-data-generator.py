#!/usr/bin/env python3
"""
Railway-compatible data generator for Grafana synthetic monitoring
This version works with Railway's PostgreSQL add-on
"""

import os
import time
import random
import json
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import requests

# Railway PostgreSQL connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Fallback for local development
    DATABASE_URL = "postgresql://grafana:password@localhost:5432/synthetic_data"

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def setup_database():
    """Setup database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS http_checks (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP DEFAULT NOW(),
            check_name VARCHAR(255),
            probe_name VARCHAR(255),
            target_url VARCHAR(500),
            response_time INTEGER,
            status_code INTEGER,
            success BOOLEAN,
            error_message TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_events (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP DEFAULT NOW(),
            event_type VARCHAR(100),
            severity VARCHAR(50),
            check_name VARCHAR(255),
            probe_name VARCHAR(255),
            message TEXT,
            metadata JSONB
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database setup complete")

def generate_http_check():
    """Generate a single HTTP check"""
    checks = [
        {"name": "api-production", "url": "https://api.example.com/health"},
        {"name": "auth-service", "url": "https://auth.example.com/status"},
        {"name": "e-commerce-site", "url": "https://shop.example.com"},
        {"name": "grafana-website", "url": "https://grafana.com"}
    ]
    
    probes = ["us-east-1", "us-west-1", "eu-central-1", "eu-west-1", "ap-southeast-1", "ap-northeast-1"]
    
    check = random.choice(checks)
    probe = random.choice(probes)
    
    # Simulate realistic response times and occasional failures
    if random.random() < 0.05:  # 5% failure rate
        response_time = random.randint(5000, 10000)
        status_code = random.choice([500, 502, 503, 504])
        success = False
        error_message = random.choice([
            "Connection timeout",
            "Internal Server Error", 
            "Service Unavailable",
            "Gateway timeout"
        ])
    else:
        response_time = random.randint(100, 500)
        status_code = 200
        success = True
        error_message = None
    
    return {
        "check_name": check["name"],
        "probe_name": probe,
        "target_url": check["url"],
        "response_time": response_time,
        "status_code": status_code,
        "success": success,
        "error_message": error_message
    }

def generate_monitoring_event():
    """Generate a monitoring event"""
    event_types = ["check_failed", "ssl_expiry_warning", "high_latency", "recovery"]
    severities = ["critical", "warning", "info"]
    checks = ["api-production", "auth-service", "e-commerce-site", "grafana-website"]
    probes = ["us-east-1", "us-west-1", "eu-central-1", "eu-west-1", "ap-southeast-1", "ap-northeast-1"]
    
    event_type = random.choice(event_types)
    severity = random.choice(severities)
    check_name = random.choice(checks)
    probe_name = random.choice(probes)
    
    messages = {
        "check_failed": f"HTTP check failed: {random.choice(['Connection timeout', 'Internal Server Error', 'Service Unavailable'])}",
        "ssl_expiry_warning": f"SSL certificate expires in {random.randint(1, 30)} days",
        "high_latency": f"Response time exceeded threshold: {random.randint(1000, 5000)}ms",
        "recovery": "Service recovered from previous failure"
    }
    
    return {
        "event_type": event_type,
        "severity": severity,
        "check_name": check_name,
        "probe_name": probe_name,
        "message": messages[event_type],
        "metadata": {"probe_region": probe_name, "timestamp": datetime.now().isoformat()}
    }

def insert_data():
    """Insert generated data into database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Generate and insert HTTP check
        http_check = generate_http_check()
        cursor.execute("""
            INSERT INTO http_checks (check_name, probe_name, target_url, response_time, status_code, success, error_message)
            VALUES (%(check_name)s, %(probe_name)s, %(target_url)s, %(response_time)s, %(status_code)s, %(success)s, %(error_message)s)
        """, http_check)
        
        # Generate and insert monitoring event (occasionally)
        if random.random() < 0.1:  # 10% chance
            event = generate_monitoring_event()
            cursor.execute("""
                INSERT INTO monitoring_events (event_type, severity, check_name, probe_name, message, metadata)
                VALUES (%(event_type)s, %(severity)s, %(check_name)s, %(probe_name)s, %(message)s, %(metadata)s)
            """, event)
        
        conn.commit()
        print(f"✅ Inserted data: {http_check['check_name']} from {http_check['probe_name']}")
        
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function"""
    print("🚀 Starting Railway Grafana Data Generator")
    
    # Setup database
    setup_database()
    
    # Generate data every 30 seconds
    while True:
        try:
            insert_data()
            time.sleep(30)
        except KeyboardInterrupt:
            print("🛑 Stopping data generator")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
