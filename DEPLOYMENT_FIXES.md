# Deployment Fixes Guide

## Issues Identified

1. **IPC Browser Not Showing Sections**: The backend isn't properly loading the IPC dataset on Render
2. **500 Error on Chat**: Communication issues between backend and AI service
3. **Environment Variables**: Missing or incorrect configuration

## Fixes Applied

### Backend Fixes

1. **Improved Dataset Loading**: Enhanced the dataset loading logic to try multiple paths
2. **Added Health Check**: Added `/health` endpoint to diagnose issues
3. **Environment Configuration**: Created `.env.production` with correct settings

### AI Service Fixes

1. **Enhanced Health Check**: Added detailed health check endpoint
2. **Environment Configuration**: Created `.env.production` with correct settings

## Required Actions on Render

### For jurisai-backend Service:

1. Set these environment variables:
   ```
   PORT=3000
   NODE_ENV=production
   MONGO_URI="mongodb+srv://GhostRider:3007%40Gamer@jurisai-sem4.zievaco.mongodb.net/jurisai?retryWrites=true&w=majority&appName=JurisAI-Sem4"
   JWT_SECRET=your-jwt-secret-key-here (generate a secure one)
   AI_SERVICE_URL=https://jurisai-ai-service.onrender.com
   CLIENT_ORIGIN=https://jurisai-ipc.vercel.app
   ```

2. Redeploy the service after setting environment variables

### For jurisai-ai-service Service:

1. Set these environment variables:
   ```
   PORT=8000
   MONGO_URI="mongodb+srv://GhostRider:3007%40Gamer@jurisai-sem4.zievaco.mongodb.net/jurisai?retryWrites=true&w=majority&appName=JurisAI-Sem4"
   JWT_SECRET=your-jwt-secret-key-here (same as backend or generate new)
   MODEL_PROVIDER=OLLAMA_CLOUD
   OLLAMA_URL=https://api.ollama.com
   OLLAMA_API_KEY=your-ollama-cloud-api-key
   OLLAMA_MODEL=qwen2.5:3b
   REDIS_URL=redis://red-d7c3k79o3t8c73dj48e0:6379
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   VECTOR_INDEX_PATH=vector_index/ipc.index
   MAX_CONTEXT_TOKENS=3000
   MAX_OUTPUT_TOKENS=500
   ```

2. Redeploy the service after setting environment variables

## Testing After Deployment

1. Check backend health: `curl https://jurisai-backend-qfn6.onrender.com/health`
2. Check AI service health: `curl https://jurisai-ai-service.onrender.com/health`
3. Test IPC browser: Visit `https://jurisai-ipc.vercel.app/ipc-browser`
4. Test chat functionality: Try asking a question in the chat interface

## Common Issues and Solutions

### If IPC Browser Still Empty:
- Check backend logs for dataset loading errors
- Ensure the dataset file is included in the deployment
- Verify the file path in the backend code

### If Chat Still Fails:
- Check that `AI_SERVICE_URL` is correctly set in backend environment variables
- Verify both services are running and accessible
- Check the logs for specific error messages

### If Environment Variables Not Persisting:
- Make sure to save environment variables in Render dashboard
- Redeploy services after setting variables
- Check that variable names match exactly