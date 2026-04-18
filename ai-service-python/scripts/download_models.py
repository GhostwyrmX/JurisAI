#!/usr/bin/env python3
"""
Script to download required Ollama models for JURIS AI
"""

import subprocess
import sys
import os
import requests
import time

def check_ollama_health():
    """Check if Ollama is running and healthy"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def wait_for_ollama(max_attempts=24):
    """Wait for Ollama to be ready"""
    print("Waiting for Ollama service to be ready...")
    for attempt in range(max_attempts):
        if check_ollama_health():
            print("Ollama is ready!")
            return True
        print(f"Attempt {attempt + 1}/{max_attempts}: Waiting for Ollama...")
        time.sleep(5)
    return False

def get_installed_models():
    """Get list of installed models"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Header line plus at least one model
                models = []
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
        return []
    except FileNotFoundError:
        print("Ollama not found. Please install Ollama first.")
        return None

def read_model_requirements():
    """Read model requirements from file"""
    requirements_file = os.path.join(os.path.dirname(__file__), "..", "models", "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print(f"Requirements file not found: {requirements_file}")
        print("Using default model: qwen2.5-coder:3b")
        return ["qwen2.5-coder:3b"]
    
    models = []
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                models.append(line)
    
    return models

def download_model(model_name):
    """Download a model using Ollama"""
    print(f"Downloading model: {model_name}")
    try:
        result = subprocess.run(["ollama", "pull", model_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully downloaded {model_name}")
            return True
        else:
            print(f"Failed to download {model_name}: {result.stderr}")
            return False
    except FileNotFoundError:
        print("Ollama not found. Please install Ollama first.")
        return False

def main():
    """Main function to download required models"""
    print("JURIS AI - Ollama Model Downloader")
    print("=" * 40)
    
    # Wait for Ollama to be ready
    if not wait_for_ollama():
        print("Ollama did not become ready in time. Please check if Ollama is running.")
        sys.exit(1)
    
    # Get installed models
    installed_models = get_installed_models()
    if installed_models is None:
        sys.exit(1)
    
    # Read required models
    required_models = read_model_requirements()
    
    # Download missing models
    downloaded_count = 0
    for model in required_models:
        if model in installed_models:
            print(f"Model {model} already installed")
        else:
            if download_model(model):
                downloaded_count += 1
    
    print(f"\nModel download complete. {downloaded_count} models downloaded.")

if __name__ == "__main__":
    main()