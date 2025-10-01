#!/usr/bin/env python3
"""
Synthetic Data Generator for Grafana
Generates realistic time-series data for demonstration purposes
"""

import os
import time
import random
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from faker import Faker
import numpy as np

fake = Faker()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'user': os.getenv('POSTGRES_USER', 'grafana'),
    'password': os.getenv('POSTGRES_PASSWORD', 'grafana'),
    'database': os.getenv('POSTGRES_DB', 'synthetic_data')
}

PUSHGATEWAY_URL = os.getenv('PROMETHEUS_PUSHGATEWAY', 'http://localhost:9091')

# Server names
SERVERS = ['web-server-01', 'web-server-02', 'api-server-01', 'api-server-02', 'db-server-01']
APPLICATIONS = ['frontend', 'backend-api', 'payment-service', 'auth-service', 'notification-service']

# Synthetic Monitoring Configuration
PROBES = ['us-east-1', 'us-west-1', 'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1']
HTTP_CHECKS = [
    {'name': 'grafana-website', 'url': 'https://grafana.com', 'expected_code': 200},
    {'name': 'api-production', 'url': 'https://api.example.com/health', 'expected_code': 200},
    {'name': 'e-commerce-site', 'url': 'https://shop.example.com', 'expected_code': 200},
    {'name': 'auth-service', 'url': 'https://auth.example.com/status', 'expected_code': 200},
]
PING_CHECKS = [
    {'name': 'dns-server-google', 'host': '8.8.8.8'},
    {'name': 'cdn-endpoint', 'host': 'cdn.example.com'},
    {'name': 'gateway', 'host': 'gateway.example.com'},
]
DNS_CHECKS = [
    {'name': 'website-dns', 'domain': 'example.com'},
    {'name': 'api-dns', 'domain': 'api.example.com'},
]
TCP_CHECKS = [
    {'name': 'postgres-db', 'host': 'db.example.com', 'port': 5432},
    {'name': 'redis-cache', 'host': 'cache.example.com', 'port': 6379},
    {'name': 'https-endpoint', 'host': 'secure.example.com', 'port': 443},
]

class SyntheticDataGenerator:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_prometheus_metrics()
        self.conn = None
        self.connect_db()
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        max_retries = 10
        for i in range(max_retries):
            try:
                self.conn = psycopg2.connect(**DB_CONFIG)
                print(f"✓ Connected to PostgreSQL database")
                return
            except psycopg2.OperationalError as e:
                print(f"Waiting for database... (attempt {i+1}/{max_retries})")
                time.sleep(5)
        raise Exception("Failed to connect to database")
    
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        self.cpu_gauge = Gauge('system_cpu_usage', 'CPU Usage Percentage', ['server'], registry=self.registry)
        self.memory_gauge = Gauge('system_memory_usage', 'Memory Usage Percentage', ['server'], registry=self.registry)
        self.disk_gauge = Gauge('system_disk_usage', 'Disk Usage Percentage', ['server'], registry=self.registry)
        self.requests_gauge = Gauge('http_requests_total', 'Total HTTP Requests', ['app', 'status'], registry=self.registry)
        self.response_time_gauge = Gauge('http_response_time_ms', 'HTTP Response Time', ['app'], registry=self.registry)
        self.active_users_gauge = Gauge('active_users', 'Active Users', ['app'], registry=self.registry)
        self.revenue_gauge = Gauge('business_revenue', 'Revenue', registry=self.registry)
        self.transactions_gauge = Gauge('business_transactions', 'Transactions', registry=self.registry)
    
    def generate_server_metrics(self):
        """Generate synthetic server metrics"""
        timestamp = datetime.now()
        cursor = self.conn.cursor()
        
        for server in SERVERS:
            # Generate realistic metrics with some variation
            base_cpu = random.uniform(20, 60)
            cpu_usage = max(0, min(100, base_cpu + np.random.normal(0, 10)))
            
            base_memory = random.uniform(40, 70)
            memory_usage = max(0, min(100, base_memory + np.random.normal(0, 5)))
            
            disk_usage = random.uniform(30, 85)
            network_in = random.uniform(100, 10000)  # KB/s
            network_out = random.uniform(50, 5000)   # KB/s
            
            # Insert into PostgreSQL
            cursor.execute("""
                INSERT INTO server_metrics (time, server_name, cpu_usage, memory_usage, disk_usage, network_in, network_out)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (timestamp, server, cpu_usage, memory_usage, disk_usage, network_in, network_out))
            
            # Update Prometheus metrics
            self.cpu_gauge.labels(server=server).set(cpu_usage)
            self.memory_gauge.labels(server=server).set(memory_usage)
            self.disk_gauge.labels(server=server).set(disk_usage)
        
        self.conn.commit()
        cursor.close()
    
    def generate_application_metrics(self):
        """Generate synthetic application metrics"""
        timestamp = datetime.now()
        cursor = self.conn.cursor()
        
        for app in APPLICATIONS:
            # Simulate traffic patterns (higher during "business hours")
            hour = timestamp.hour
            traffic_multiplier = 1.5 if 9 <= hour <= 17 else 0.7
            
            request_count = int(random.uniform(100, 1000) * traffic_multiplier)
            error_rate = random.uniform(0.01, 0.05)
            error_count = int(request_count * error_rate)
            response_time = max(10, random.gauss(150, 50))  # ms
            active_users = int(random.uniform(50, 500) * traffic_multiplier)
            
            # Insert into PostgreSQL
            cursor.execute("""
                INSERT INTO application_metrics (time, app_name, request_count, error_count, response_time, active_users)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (timestamp, app, request_count, error_count, response_time, active_users))
            
            # Update Prometheus metrics
            self.requests_gauge.labels(app=app, status='200').set(request_count - error_count)
            self.requests_gauge.labels(app=app, status='500').set(error_count)
            self.response_time_gauge.labels(app=app).set(response_time)
            self.active_users_gauge.labels(app=app).set(active_users)
        
        self.conn.commit()
        cursor.close()
    
    def generate_business_metrics(self):
        """Generate synthetic business metrics"""
        timestamp = datetime.now()
        cursor = self.conn.cursor()
        
        # Simulate business metrics
        revenue = max(0, random.gauss(5000, 1000))
        transactions = int(random.uniform(50, 300))
        conversion_rate = random.uniform(0.02, 0.08)
        
        cursor.execute("""
            INSERT INTO business_metrics (time, metric_type, revenue, transactions, conversion_rate)
            VALUES (%s, %s, %s, %s, %s)
        """, (timestamp, 'sales', revenue, transactions, conversion_rate))
        
        self.conn.commit()
        cursor.close()
        
        # Update Prometheus metrics
        self.revenue_gauge.set(revenue)
        self.transactions_gauge.set(transactions)
    
    def push_to_prometheus(self):
        """Push metrics to Prometheus Pushgateway"""
        try:
            push_to_gateway(PUSHGATEWAY_URL.replace('http://', ''), job='synthetic_data', registry=self.registry)
        except Exception as e:
            print(f"⚠ Failed to push to Prometheus: {e}")
    
    def generate_http_checks(self):
        """Generate synthetic HTTP check data"""
        timestamp = datetime.now()
        cursor = self.conn.cursor()
        
        for check in HTTP_CHECKS:
            for probe in PROBES:
                # Simulate check results with occasional failures
                failure_chance = 0.02  # 2% failure rate
                is_success = random.random() > failure_chance
                
                if is_success:
                    status_code = check['expected_code']
                    response_time = max(10, random.gauss(150, 50))  # Normal response time
                    error_msg = None
                else:
                    # Simulate various failure types
                    failure_types = [
                        (500, 'Internal Server Error'),
                        (502, 'Bad Gateway'),
                        (503, 'Service Unavailable'),
                        (0, 'Connection timeout'),
                        (0, 'DNS resolution failed'),
                    ]
                    status_code, error_msg = random.choice(failure_types)
                    response_time = random.uniform(5000, 10000) if status_code > 0 else None
                
                # Add regional latency variation
                region_latency = {'us-east-1': 0, 'us-west-1': 20, 'eu-west-1': 80, 
                                'eu-central-1': 90, 'ap-southeast-1': 150, 'ap-northeast-1': 160}
                if response_time:
                    response_time += region_latency.get(probe, 0)
                
                ssl_expiry = random.randint(30, 365) if is_success else None
                dns_time = max(5, random.gauss(20, 10)) if is_success else None
                connect_time = max(10, random.gauss(50, 20)) if is_success else None
                
                cursor.execute("""
                    INSERT INTO http_checks (time, check_name, target_url, probe_name, status_code, 
                                           response_time_ms, success, ssl_expiry_days, dns_time_ms, 
                                           connect_time_ms, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (timestamp, check['name'], check['url'], probe, status_code, response_time, 
                      is_success, ssl_expiry, dns_time, connect_time, error_msg))
                
                # Generate event if check failed
                if not is_success:
                    self.generate_monitoring_event(cursor, timestamp, 'check_failed', 'critical',
                                                  check['name'], probe, 
                                                  f"HTTP check failed: {error_msg}",
                                                  {'url': check['url'], 'status_code': status_code})
                # Generate warning if SSL expires soon
                elif ssl_expiry and ssl_expiry < 30:
                    self.generate_monitoring_event(cursor, timestamp, 'ssl_expiring', 'warning',
                                                  check['name'], probe,
                                                  f"SSL certificate expires in {ssl_expiry} days",
                                                  {'url': check['url'], 'days_remaining': ssl_expiry})
                # Generate warning if response time is high
                elif response_time and response_time > 1000:
                    self.generate_monitoring_event(cursor, timestamp, 'high_latency', 'warning',
                                                  check['name'], probe,
                                                  f"High response time: {response_time:.0f}ms",
                                                  {'url': check['url'], 'response_time': response_time})
        
        self.conn.commit()
        cursor.close()
    
    def generate_ping_checks(self):
        """Generate synthetic ping/ICMP check data"""
        timestamp = datetime.now()
        cursor = self.conn.cursor()
        
        for check in PING_CHECKS:
            for probe in PROBES:
                failure_chance = 0.01  # 1% failure rate
                is_success = random.random() > failure_chance
                
                if is_success:
                    latency = max(1, random.gauss(30, 15))
                    packet_loss = random.choice([0, 0, 0, 0, 0.1, 0.5])  # Usually 0
                    error_msg = None
                else:
                    latency = None
                    packet_loss = random.uniform(50, 100)
                    error_msg = random.choice(['Request timeout', 'Host unreachable', 'Network unreachable'])
                
                cursor.execute("""
                    INSERT INTO ping_checks (time, check_name, target_host, probe_name, latency_ms, 
                                           packet_loss, success, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (timestamp, check['name'], check['host'], probe, latency, packet_loss, is_success, error_msg))
                
                if not is_success or packet_loss > 10:
                    severity = 'critical' if not is_success else 'warning'
                    self.generate_monitoring_event(cursor, timestamp, 'ping_failed', severity,
                                                  check['name'], probe,
                                                  f"Ping check issue: {error_msg or f'{packet_loss}% packet loss'}",
                                                  {'host': check['host'], 'packet_loss': packet_loss})
        
        self.conn.commit()
        cursor.close()
    
    def generate_dns_checks(self):
        """Generate synthetic DNS check data"""
        timestamp = datetime.now()
        cursor = self.conn.cursor()
        
        for check in DNS_CHECKS:
            for probe in PROBES:
                failure_chance = 0.005  # 0.5% failure rate
                is_success = random.random() > failure_chance
                
                if is_success:
                    resolution_time = max(5, random.gauss(25, 10))
                    resolved_ips = [fake.ipv4() for _ in range(random.randint(1, 3))]
                    error_msg = None
                else:
                    resolution_time = None
                    resolved_ips = []
                    error_msg = random.choice(['NXDOMAIN', 'SERVFAIL', 'Timeout'])
                
                cursor.execute("""
                    INSERT INTO dns_checks (time, check_name, target_domain, probe_name, resolution_time_ms,
                                          success, resolved_ips, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (timestamp, check['name'], check['domain'], probe, resolution_time, 
                      is_success, resolved_ips, error_msg))
                
                if not is_success:
                    self.generate_monitoring_event(cursor, timestamp, 'dns_failed', 'critical',
                                                  check['name'], probe,
                                                  f"DNS resolution failed: {error_msg}",
                                                  {'domain': check['domain']})
        
        self.conn.commit()
        cursor.close()
    
    def generate_tcp_checks(self):
        """Generate synthetic TCP check data"""
        timestamp = datetime.now()
        cursor = self.conn.cursor()
        
        for check in TCP_CHECKS:
            for probe in PROBES:
                failure_chance = 0.015  # 1.5% failure rate
                is_success = random.random() > failure_chance
                
                if is_success:
                    connect_time = max(5, random.gauss(40, 20))
                    error_msg = None
                else:
                    connect_time = None
                    error_msg = random.choice(['Connection refused', 'Connection timeout', 'Network unreachable'])
                
                cursor.execute("""
                    INSERT INTO tcp_checks (time, check_name, target_host, target_port, probe_name,
                                          connect_time_ms, success, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (timestamp, check['name'], check['host'], check['port'], probe, 
                      connect_time, is_success, error_msg))
                
                if not is_success:
                    self.generate_monitoring_event(cursor, timestamp, 'tcp_failed', 'critical',
                                                  check['name'], probe,
                                                  f"TCP connection failed: {error_msg}",
                                                  {'host': check['host'], 'port': check['port']})
        
        self.conn.commit()
        cursor.close()
    
    def generate_monitoring_event(self, cursor, timestamp, event_type, severity, check_name, probe_name, message, details):
        """Generate a monitoring event/alert"""
        cursor.execute("""
            INSERT INTO monitoring_events (time, event_type, severity, check_name, probe_name, message, details, resolved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (timestamp, event_type, severity, check_name, probe_name, message, 
              psycopg2.extras.Json(details), False))
    
    def generate_historical_data(self, hours=24):
        """Generate historical data for the past N hours"""
        print(f"Generating {hours} hours of historical data...")
        cursor = self.conn.cursor()
        
        current_time = datetime.now()
        for i in range(hours * 60):  # Generate data every minute
            timestamp = current_time - timedelta(minutes=i)
            
            # Server metrics
            for server in SERVERS:
                cpu_usage = max(0, min(100, random.uniform(20, 80)))
                memory_usage = max(0, min(100, random.uniform(40, 70)))
                disk_usage = random.uniform(30, 85)
                network_in = random.uniform(100, 10000)
                network_out = random.uniform(50, 5000)
                
                cursor.execute("""
                    INSERT INTO server_metrics (time, server_name, cpu_usage, memory_usage, disk_usage, network_in, network_out)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (timestamp, server, cpu_usage, memory_usage, disk_usage, network_in, network_out))
            
            # Application metrics
            for app in APPLICATIONS:
                hour = timestamp.hour
                traffic_multiplier = 1.5 if 9 <= hour <= 17 else 0.7
                
                request_count = int(random.uniform(100, 1000) * traffic_multiplier)
                error_count = int(request_count * random.uniform(0.01, 0.05))
                response_time = max(10, random.gauss(150, 50))
                active_users = int(random.uniform(50, 500) * traffic_multiplier)
                
                cursor.execute("""
                    INSERT INTO application_metrics (time, app_name, request_count, error_count, response_time, active_users)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, app, request_count, error_count, response_time, active_users))
            
            # Business metrics
            revenue = max(0, random.gauss(5000, 1000))
            transactions = int(random.uniform(50, 300))
            conversion_rate = random.uniform(0.02, 0.08)
            
            cursor.execute("""
                INSERT INTO business_metrics (time, metric_type, revenue, transactions, conversion_rate)
                VALUES (%s, %s, %s, %s, %s)
            """, (timestamp, 'sales', revenue, transactions, conversion_rate))
            
            if i % 60 == 0:
                print(f"  Generated data for {i // 60} hours ago...")
        
        self.conn.commit()
        cursor.close()
        print("✓ Historical data generation complete")
    
    def run(self):
        """Main loop to generate data"""
        print("Starting Synthetic Data Generator...")
        
        # Generate historical data on first run
        self.generate_historical_data(hours=24)
        
        print("Starting real-time data generation...")
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generating data (iteration {iteration})...")
                
                # Generate infrastructure metrics
                self.generate_server_metrics()
                self.generate_application_metrics()
                self.generate_business_metrics()
                
                # Generate synthetic monitoring data
                self.generate_http_checks()
                self.generate_ping_checks()
                self.generate_dns_checks()
                self.generate_tcp_checks()
                
                self.push_to_prometheus()
                
                print("✓ Data generated successfully")
                time.sleep(15)  # Generate new data every 15 seconds
                
            except KeyboardInterrupt:
                print("\n\nStopping data generator...")
                break
            except Exception as e:
                print(f"✗ Error generating data: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)
        
        if self.conn:
            self.conn.close()

if __name__ == '__main__':
    generator = SyntheticDataGenerator()
    generator.run()

