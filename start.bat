@echo off
REM JURIS AI - Startup Script for Windows

echo Starting JURIS AI - Legal Intelligence Platform

REM Check if required services are running
echo Checking prerequisites...

REM Check if MongoDB is running
netstat -an | findstr ":27017" >nul
if %errorlevel% neq 0 (
    echo MongoDB is not running. Please start MongoDB first.
    pause
    exit /b 1
)

REM Check if Redis is running
netstat -an | findstr ":6379" >nul
if %errorlevel% neq 0 (
    echo Redis is not running. Please start Redis first.
    pause
    exit /b 1
)

REM Check if Ollama is running
netstat -an | findstr ":11434" >nul
if %errorlevel% neq 0 (
    echo Ollama is not running. Please start Ollama first.
    pause
    exit /b 1
)

echo All prerequisites are satisfied.

REM Start Python AI Service
echo Starting Python AI Service...
cd ai-service-python
start "Python AI Service" cmd /k "python main.py"
cd ..

REM Start Node.js Backend
echo Starting Node.js Backend...
cd backend-node
start "Node.js Backend" cmd /k "npm start"
cd ..

REM Start React Frontend
echo Starting React Frontend...
cd frontend
start "React Frontend" cmd /k "npm start"
cd ..

echo JURIS AI is now running!
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:3000
echo AI Service API: http://localhost:8000
echo.
echo Note: If this is the first time running the system, it may take a few minutes
echo for all services to initialize and for models to download.

pause