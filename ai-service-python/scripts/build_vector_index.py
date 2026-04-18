import sys
import os

# Add parent directory to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from services.rag_service import RAGService
from utils.logging import log_info, log_error

def build_vector_index():
    """Build FAISS vector index from IPC dataset"""
    try:
        log_info("Starting vector index build process")
        
        # Initialize RAG service which will build the index
        rag_service = RAGService()
        rag_service.build_vector_index()
        
        log_info("Vector index build completed successfully")
        return True
        
    except Exception as e:
        log_error(f"Vector index build failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = build_vector_index()
    if success:
        log_info("Vector index build completed successfully")
    else:
        log_error("Vector index build failed")
        sys.exit(1)