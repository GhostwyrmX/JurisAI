# Service Setup Guide

This guide covers the local services needed by JURIS AI.

## Required Services

- MongoDB
- Redis
- Ollama

## MongoDB

### Verify MongoDB

```bash
mongo
```

Default connection:

```text
mongodb://localhost:27017/juris_ai
```

## Redis

### Verify Redis

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

Default connection:

```text
redis://localhost:6379
```

## Ollama

### Start Ollama

```bash
ollama serve
```

### Install the Main Model

```bash
ollama pull qwen2.5-coder:7b
```

### Verify Installed Models

```bash
ollama list
```

## Environment Configuration

`ai-service-python/.env`

```env
MONGO_URI=mongodb://localhost:27017/juris_ai
REDIS_URL=redis://localhost:6379
OLLAMA_URL=http://localhost:11434
MODEL_PROVIDER=OLLAMA_LOCAL
EMBEDDING_MODEL=bge-large-en
VECTOR_INDEX_PATH=vector_index/ipc.index
```

`backend-node/.env`

```env
MONGO_URI=mongodb://localhost:27017/juris_ai
AI_SERVICE_URL=http://localhost:8000
JWT_SECRET=supersecret
PORT=3000
```

`frontend/.env`

```env
REACT_APP_API_URL=http://localhost:3000
```

## Dataset Preparation

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

## Start Order

1. MongoDB
2. Redis
3. Ollama
4. Python AI service
5. Node backend
6. React frontend

## App Startup Commands

```bash
cd ai-service-python
python main.py
```

```bash
cd backend-node
npm start
```

```bash
cd frontend
npm start
```

## Troubleshooting

### AI responses do not reflect dataset changes

Re-run:

```bash
python scripts/ingest_dataset.py
python scripts/build_vector_index.py
```

### Scenario confidence feels too low or stale

Restart the Python AI service after updating `charge_prediction.py`.

### Voice-to-text is unavailable

- Use Chrome or Edge
- Make sure microphone permission is allowed
- Check that the page is loaded in a browser with Web Speech API support

### Frontend does not fit the device width

- Restart the frontend after pulling UI changes
- Clear browser cache if old CSS is still being served
