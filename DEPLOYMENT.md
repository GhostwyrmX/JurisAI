# Deployment Guide

## Recommended Setup

Use a split deployment:

- Deploy `frontend/` to Vercel
- Deploy `Dockerfile.backend` to a container platform like Render, Railway, Fly.io, or a VPS
- Deploy `Dockerfile.ai-service` to a container platform
- Use a managed MongoDB and Redis instance
- Point `AI_SERVICE_URL` from the backend to the deployed AI service
- Point `REACT_APP_API_URL` in Vercel to the deployed backend URL

This is the recommended path because the AI service depends on FAISS, Redis, and Ollama, which are not a good fit for Vercel serverless functions.

## Alternate Setup

Use a non-Vercel container platform for the full app:

- Deploy `Dockerfile.backend`
- Deploy `Dockerfile.ai-service`
- The backend image already builds the React frontend and serves it from Express
- In this mode, the frontend does not need a separate deployment

## Environment Variables

### Frontend

`REACT_APP_API_URL`

Example:

```env
REACT_APP_API_URL=https://your-backend.example.com
```

### Backend

```env
PORT=3000
MONGO_URI=your-mongodb-connection-string
JWT_SECRET=your-secret
AI_SERVICE_URL=https://your-ai-service.example.com
CLIENT_ORIGIN=https://your-frontend.example.com
```

### AI Service

```env
PORT=8000
MONGO_URI=your-mongodb-connection-string
JWT_SECRET=your-secret
MODEL_PROVIDER=OLLAMA_LOCAL
OLLAMA_URL=http://your-ollama-host:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_API_KEY=your-ollama-api-key-if-using-cloud
REDIS_URL=your-redis-connection-string
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_INDEX_PATH=vector_index/ipc.index
MAX_CONTEXT_TOKENS=3000
MAX_OUTPUT_TOKENS=500
```

## Vercel Frontend

Deploy the `frontend` directory as the Vercel project root.

Build settings:

- Install command: `npm install`
- Build command: `npm run build`
- Output directory: `build`

The included [`frontend/vercel.json`](./frontend/vercel.json) handles React Router rewrites.

## Container Notes

- `Dockerfile.backend` now builds the React frontend and serves it from Express
- `Dockerfile.frontend` builds a standalone static frontend image
- `Dockerfile.ai-service` now respects the platform `PORT` variable

## Important Limitation

If you keep `MODEL_PROVIDER=OLLAMA_LOCAL`, the AI service still needs access to a running Ollama instance. For cloud deployment, that usually means:

- host Ollama on a separate VM/GPU box and set `OLLAMA_URL` to it, or
- replace the LLM provider implementation with a hosted model API

If you use Ollama Cloud, set:

- `OLLAMA_URL=https://ollama.com`
- `OLLAMA_API_KEY` to your Ollama API key
