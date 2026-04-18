#!/bin/bash

# Script to initialize Ollama with required models from requirements file

echo "Starting Ollama model initialization..."

# Wait for Ollama to be ready
echo "Waiting for Ollama service to be ready..."
until curl -s http://localhost:11434/api/tags >/dev/null 2>&1; do
    sleep 5
    echo "Waiting for Ollama..."
done

echo "Ollama is ready. Checking for required models..."

# Read models from requirements file
MODELS_FILE="./ai-service-python/models/requirements.txt"

if [ ! -f "$MODELS_FILE" ]; then
    echo "Models requirements file not found: $MODELS_FILE"
    echo "Downloading default model: qwen2.5-coder:7b"
    ollama pull qwen2.5-coder:7b
    echo "Model download complete!"
    exit 0
fi

# Process each model in the requirements file
while IFS= read -r model || [[ -n "$model" ]]; do
    # Skip empty lines and comments
    if [[ -z "$model" ]] || [[ "$model" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Remove leading/trailing whitespace
    model=$(echo "$model" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    # Skip if empty after trimming
    if [[ -z "$model" ]]; then
        continue
    fi
    
    echo "Checking model: $model"
    
    # Check if model exists
    if curl -s http://localhost:11434/api/tags | grep -q "\"$model\""; then
        echo "$model model already exists"
    else
        echo "Downloading $model model..."
        ollama pull "$model"
        if [ $? -eq 0 ]; then
            echo "$model model download complete!"
        else
            echo "Failed to download $model model"
        fi
    fi
done < "$MODELS_FILE"

echo "Ollama initialization complete!"