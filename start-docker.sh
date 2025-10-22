#!/bin/bash

# 5500 Backend Docker Startup Script
# This script starts the full stack: backend + database + pgAdmin

echo "🚀 Starting 5500 Full Stack (Backend + Database + pgAdmin)..."

# Build and start all services
docker-compose up -d --build

echo "⏳ Waiting for services to be ready..."
sleep 30

echo "🔍 Checking database connection..."
until docker exec 5500_database pg_isready -U qr_survey_user -d qr_survey_db; do 
    echo "Waiting for database..."; 
    sleep 2; 
done

echo "🔄 Running database migrations..."
docker-compose exec backend uv run alembic upgrade head

echo "🌱 Seeding database..."
docker-compose exec backend uv run python scripts/seed.py

echo ""
echo "✅ Full 5500 stack is running!"
echo "🚀 Backend API: http://localhost:8000"
echo "📊 Database: localhost:5432"
echo "🌐 pgAdmin: http://localhost:5050"
echo "📋 pgAdmin Login: admin@qrsurvey.com / admin_password"
echo ""
echo "📋 To view logs: docker-compose logs -f"
echo "📋 To stop: docker-compose down"
echo ""
