import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/juris_ai")
    
    # JWT configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
    
    # Model provider configuration
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "OLLAMA_LOCAL")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
    OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    
    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Embedding model configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Vector index path
    VECTOR_INDEX_PATH = os.getenv("VECTOR_INDEX_PATH", "vector_index/ipc.index")
    
    # Token limits
    MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "3000"))
    MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "500"))
    
    # Legal mode configuration
    LEGAL_MODE = os.getenv("LEGAL_MODE", "IPC_ONLY")
    
    # Legal acts registry
    LEGAL_ACTS = {
        "IPC": {
            "dataset": "dataset/ipc/ipc.json",
            "vector_index": "vector_index/ipc.index"
        }
    }
