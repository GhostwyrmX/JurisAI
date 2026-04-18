# JURIS AI

JURIS AI is an IPC-focused legal intelligence platform built with a React frontend, a Node.js backend, and a Python AI service.

## Current Capabilities

- IPC-only legal question answering grounded in the dataset
- Scenario-based IPC charge prediction with calibrated confidence scores
- IPC browser with richer metadata such as category, subcategory, severity, synonyms, legal elements, related sections, and citation details
- Multilingual responses
- Text-to-speech output
- Browser-based speech-to-text input on the AI Assistant page
- Query history with detailed response cards
- Responsive frontend layouts for mobile and desktop

## Architecture

```text
React Frontend -> Node.js Backend -> Python AI Service
                                 -> MongoDB
                                 -> Redis
                                 -> FAISS Vector Index
                                 -> Ollama
```

## Main Services

### Frontend

- React
- Tailwind CSS
- Responsive pages for chat, history, browser, auth, dashboard, and profile
- Browser speech recognition for human voice-to-text

### Backend

- Express
- JWT auth
- MongoDB persistence for users and query history
- Proxy routes for AI service operations

### AI Service

- FastAPI
- Sentence Transformers embeddings
- FAISS similarity search
- Ollama-based response generation
- Scenario charge prediction
- Translation and text-to-speech

## Dataset Coverage

The current system uses a much larger portion of the IPC dataset schema than before, including:

- `section_number`
- `title`
- `chapter`
- `description`
- `section_text`
- `crime_category`
- `crime_subcategory`
- `severity_level`
- `legal_elements`
- `keywords`
- `synonyms`
- `punishment`
- `example_scenarios`
- `scenario_training`
- `related_sections`
- `crime_type_mapping`
- `court_judgment_links`
- `vector_search_terms`
- `citation`

## Setup

### Prerequisites

- Node.js 14+
- Python 3.8+
- MongoDB
- Redis
- Ollama

### Install Dependencies

```bash
cd ai-service-python
pip install -r requirements.txt

cd ../backend-node
npm install

cd ../frontend
npm install
```

### Environment Files

`ai-service-python/.env`

```env
MONGO_URI=mongodb://localhost:27017/juris_ai
JWT_SECRET=supersecret
MODEL_PROVIDER=OLLAMA_LOCAL
OLLAMA_URL=http://localhost:11434
REDIS_URL=redis://localhost:6379
EMBEDDING_MODEL=bge-large-en
VECTOR_INDEX_PATH=vector_index/ipc.index
MAX_CONTEXT_TOKENS=3000
MAX_OUTPUT_TOKENS=500
```

`backend-node/.env`

```env
MONGO_URI=mongodb://localhost:27017/juris_ai
JWT_SECRET=supersecret
AI_SERVICE_URL=http://localhost:8000
PORT=3000
```

`frontend/.env`

```env
REACT_APP_API_URL=http://localhost:3000
```

### Prepare Data

Place the IPC dataset at:

```text
dataset/ipc/ipc.json
```

Then run:

```bash
cd ai-service-python
python scripts/ingest_dataset.py
python scripts/build_vector_index.py
```

## Run the App

### Start Infrastructure

- Start MongoDB
- Start Redis
- Start Ollama with `ollama serve`

### Start Application Services

```bash
cd ai-service-python
python main.py

cd ../backend-node
npm start

cd ../frontend
npm start
```

## Key Endpoints

### Node Backend

- `POST /signup`
- `POST /login`
- `POST /chat`
- `GET /history`
- `DELETE /history`
- `DELETE /query/:queryId`
- `GET /ipc-sections`
- `GET /ipc-section/:section`
- `GET /ipc-section/:section/related`

### Python AI Service

- `POST /rag`
- `POST /predict-charges`
- `POST /generate-audio`
- `POST /tts`
- `GET /ipc-sections`
- `GET /ipc-section/{section_number}`
- `GET /ipc-section/{section_number}/related`

## Notes

- The AI system is intentionally constrained to the IPC dataset.
- Voice-to-text depends on browser support and works best in Chromium-based browsers.
- After dataset schema changes, re-run ingestion and vector index build steps.

## Deployment

Deployment instructions are available in [`DEPLOYMENT.md`](./DEPLOYMENT.md).

Recommended production setup:

- Deploy `frontend/` to Vercel
- Deploy `Dockerfile.backend` to a container platform
- Deploy `Dockerfile.ai-service` to a container platform
- Use managed MongoDB and Redis
