#!/bin/bash

# Grafana Synthetic Data Demo - Quick Start Script

echo "🚀 Starting Grafana Synthetic Data Demo..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Start services
echo "📦 Starting services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Services started successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Access Points"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 Grafana:     http://localhost:3000"
    echo "   Username:    admin"
    echo "   Password:    admin"
    echo ""
    echo "📈 Prometheus:  http://localhost:9090"
    echo "🗄️  PostgreSQL:  localhost:5432"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "ℹ️  First startup notes:"
    echo "   • The data generator will create 24 hours of"
    echo "     historical data (~2 minutes)"
    echo "   • Then it will generate real-time data every"
    echo "     15 seconds"
    echo ""
    echo "📝 View logs with: docker-compose logs -f"
    echo "🛑 Stop with: docker-compose down"
    echo ""
    echo "Opening Grafana in your browser..."
    sleep 5
    
    # Try to open browser (cross-platform)
    if command -v open &> /dev/null; then
        open http://localhost:3000
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    elif command -v start &> /dev/null; then
        start http://localhost:3000
    fi
else
    echo ""
    echo "❌ Failed to start services. Check the error messages above."
    exit 1
fi

