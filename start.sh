#!/bin/bash

# JURIS AI - Startup Script

echo "Starting JURIS AI - Legal Intelligence Platform"

# Check if required services are running
echo "Checking prerequisites..."

# Check if MongoDB is running
if ! nc -z localhost 27017; then
  echo "MongoDB is not running. Please start MongoDB first."
  exit 1
fi

# Check if Redis is running
if ! nc -z localhost 6379; then
  echo "Redis is not running. Please start Redis first."
  exit 1
fi

# Check if Ollama is running
if ! nc -z localhost 11434; then
  echo "Ollama is not running. Please start Ollama first."
  exit 1
fi

echo "All prerequisites are satisfied."

# Start Python AI Service
echo "Starting Python AI Service..."
cd ai-service-python
python main.py &
PYTHON_PID=$!
cd ..

# Start Node.js Backend
echo "Starting Node.js Backend..."
cd backend-node
npm start &
NODE_PID=$!
cd ..

# Start React Frontend
echo "Starting React Frontend..."
cd frontend
npm start &
REACT_PID=$!
cd ..

echo "JURIS AI is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:3000"
echo "AI Service API: http://localhost:8000"
echo ""
echo "Note: If this is the first time running the system, it may take a few minutes"
echo "for all services to initialize and for models to download."

# Wait for processes to complete
wait $PYTHON_PID
wait $NODE_PID
wait $REACT_PID