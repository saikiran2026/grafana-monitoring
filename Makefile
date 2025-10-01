.PHONY: help start stop restart logs clean status

help:
	@echo "Grafana Synthetic Data Demo - Available Commands:"
	@echo ""
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs from all services"
	@echo "  make status    - Show status of all services"
	@echo "  make clean     - Stop services and remove all data"
	@echo ""
	@echo "Access Grafana at: http://localhost:3000 (admin/admin)"

start:
	@echo "🚀 Starting Grafana Synthetic Data Demo..."
	docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo ""
	@echo "📊 Grafana: http://localhost:3000"
	@echo "📈 Prometheus: http://localhost:9090"
	@echo "🗄️  PostgreSQL: localhost:5432"
	@echo ""
	@echo "Login to Grafana with: admin/admin"
	@echo ""
	@echo "ℹ️  First startup will generate 24 hours of historical data (~2 minutes)"
	@echo "   View progress with: make logs"

stop:
	@echo "🛑 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped"

restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted"

logs:
	docker-compose logs -f

status:
	@echo "📊 Service Status:"
	@docker-compose ps

clean:
	@echo "⚠️  This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "🧹 Cleaning up..."; \
		docker-compose down -v; \
		echo "✅ All data removed"; \
	else \
		echo "❌ Cancelled"; \
	fi

