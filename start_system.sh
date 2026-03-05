#!/bin/bash

# Start MQTT broker and applications in correct order

echo "🚀 Starting PrecisionPulse System..."

# Kill any existing processes
pkill -f mosquitto
pkill -f "python.*run.py"
pkill -f "npm.*dev"

# Start Mosquitto MQTT broker
echo "📡 Starting MQTT broker..."
mosquitto -d -p 1883

# Wait for broker to start
sleep 2

# Start backend
echo "🔧 Starting backend..."
cd backend
python run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "🌐 Starting frontend..."
cd ../dspl-precision-pulse-frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ System started successfully!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access points:"
echo "- Web App: http://localhost:3000"
echo "- Backend API: http://localhost:5000"
echo "- MQTT Broker: localhost:1883"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; pkill -f mosquitto; exit' INT
wait