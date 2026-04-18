#!/bin/bash

# JURIS AI - Setup Script

echo "Setting up JURIS AI - Legal Intelligence Platform"

# Check if we're in the correct directory
if [ ! -f "README.md" ]; then
  echo "Please run this script from the JURIS AI root directory"
  exit 1
fi

# Setup Python AI Service
echo "Setting up Python AI Service..."
cd ai-service-python
pip install -r requirements.txt

# Download required models
echo "Downloading required models..."
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('bge-large-en')"

cd ..

# Setup Node.js Backend
echo "Setting up Node.js Backend..."
cd backend-node
npm install
cd ..

# Setup React Frontend
echo "Setting up React Frontend..."
cd frontend
npm install
cd ..

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure MongoDB, Redis, and Ollama are running"
echo "2. Configure environment variables in each service's .env file"
echo "3. Place your IPC.json dataset in dataset/ipc/"
echo "4. Run the data ingestion script: python ai-service-python/scripts/ingest_dataset.py"
echo "5. Build the vector index: python ai-service-python/scripts/build_vector_index.py"
echo "6. Download required models: python ai-service-python/scripts/download_models.py"
echo "7. Start the services using start.sh or start.bat"