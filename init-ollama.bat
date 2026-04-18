@echo off
setlocal enabledelayedexpansion
REM Script to initialize Ollama with required models from requirements file

echo Starting Ollama model initialization...

REM Wait for Ollama to be ready
echo Waiting for Ollama service to be ready...
:wait_loop
timeout /t 5 /nobreak >nul
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 goto wait_loop

echo Ollama is ready. Checking for required models...

REM Check if models requirements file exists
set MODELS_FILE=ai-service-python\models\requirements.txt
if not exist "%MODELS_FILE%" (
    echo Models requirements file not found: %MODELS_FILE%
    echo Downloading default model: qwen2.5:3b
    ollama pull qwen2.5:3b
    echo Model download complete!
    goto finish
)

REM Process each model in the requirements file
for /f "tokens=*" %%i in ('type "%MODELS_FILE%" ^| findstr /v "^#" ^| findstr /v "^$"') do (
    set model=%%i
    REM Trim whitespace
    for /f "tokens=* delims= " %%a in ("%%i") do set "trimmed_model=%%a"
    if not "!trimmed_model!"=="" (
        echo Checking model: !trimmed_model!
        
        REM Check if model exists
        curl -s http://localhost:11434/api/tags | findstr "!trimmed_model!" >nul
        if !errorlevel! equ 0 (
            echo !trimmed_model! model already exists
        ) else (
            echo Downloading !trimmed_model! model...
            ollama pull "!trimmed_model!"
            if !errorlevel! equ 0 (
                echo !trimmed_model! model download complete!
            ) else (
                echo Failed to download !trimmed_model! model
            )
        )
    )
)

:finish
echo Ollama initialization complete!
pause