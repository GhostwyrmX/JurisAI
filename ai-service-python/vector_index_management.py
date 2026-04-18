"""
FAISS Vector Index Management for IPC Sections
Implementation for research paper - demonstrates vector index creation and management
"""

import faiss
import numpy as np
import json
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
import os
from pathlib import Path
import logging
from datetime import datetime


class IPCVectorIndexManager:
    """
    Manages FAISS vector index for IPC sections with comprehensive document representation
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_dim: int = 384):
        self.model = SentenceTransformer(model_name)
        self.index_dim = index_dim
        self.index = None
        self.section_metadata = []
        self.logger = logging.getLogger(__name__)
        
    def create_composite_document(self, section_data: Dict[str, Any]) -> str:
        """
        Create comprehensive document representation for embedding
        Combines multiple IPC section fields for rich semantic representation
        """
        composite_parts = [
            f"Section {section_data.get('section_number', '')}",
            section_data.get('title', ''),
            section_data.get('description', ''),
            section_data.get('legal_elements', ''),
            section_data.get('punishment', ''),
            section_data.get('keywords', ''),
            section_data.get('category', ''),
            section_data.get('severity', '')
        ]
        
        # Filter out empty parts and join with semantic separators
        return " | ".join(filter(None, composite_parts))
    
    def build_vector_index(self, ipc_dataset_path: str, index_save_path: str) -> None:
        """
        Build FAISS index from IPC JSON dataset with comprehensive validation
        """
        try:
            # Load and validate IPC dataset
            with open(ipc_dataset_path, 'r', encoding='utf-8') as f:
                ipc_data = json.load(f)
            
            if not isinstance(ipc_data, list):
                raise ValueError("IPC dataset should be a list of sections")
            
            self.logger.info(f"Processing {len(ipc_data)} IPC sections")
            
            # Generate composite documents and embeddings
            composite_docs = []
            embeddings_list = []
            
            for section in ipc_data:
                composite_doc = self.create_composite_document(section)
                composite_docs.append(composite_doc)
                
                # Store metadata for retrieval
                self.section_metadata.append({
                    'section_number': section.get('section_number'),
                    'title': section.get('title'),
                    'category': section.get('category'),
                    'severity': section.get('severity'),
                    'composite_doc': composite_doc
                })
            
            # Generate embeddings in batches for memory efficiency
            batch_size = 32
            for i in range(0, len(composite_docs), batch_size):
                batch_docs = composite_docs[i:i + batch_size]
                batch_embeddings = self.model.encode(batch_docs, convert_to_numpy=True)
                embeddings_list.append(batch_embeddings)
            
            # Concatenate all embeddings
            all_embeddings = np.vstack(embeddings_list)
            
            # Create and train FAISS index
            self.index = faiss.IndexFlatL2(self.index_dim)
            self.index.add(all_embeddings)
            
            # Save index and metadata
            self._save_index(index_save_path, all_embeddings)
            
            self.logger.info(f"Vector index built successfully with {len(ipc_data)} sections")
            
        except Exception as e:
            self.logger.error(f"Error building vector index: {str(e)}")
            raise
    
    def _save_index(self, save_path: str, embeddings: np.ndarray) -> None:
        """Save index and metadata to disk"""
        # Create directory if it doesn't exist
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(save_path, "ipc.index"))
        
        # Save metadata
        metadata = {
            'section_metadata': self.section_metadata,
            'embedding_dim': self.index_dim,
            'total_sections': len(self.section_metadata),
            'created_at': datetime.now().isoformat(),
            'model_name': self.model._modules['0'].auto_model.config.name_or_path
        }
        
        with open(os.path.join(save_path, "ipc.metadata.pkl"), 'wb') as f:
            pickle.dump(metadata, f)
        
        # Save embeddings for potential reuse
        np.save(os.path.join(save_path, "embeddings.npy"), embeddings)
    
    def load_index(self, index_path: str) -> None:
        """Load pre-built index from disk"""
        try:
            self.index = faiss.read_index(os.path.join(index_path, "ipc.index"))
            
            with open(os.path.join(index_path, "ipc.metadata.pkl"), 'rb') as f:
                metadata = pickle.load(f)
                self.section_metadata = metadata['section_metadata']
            
            self.logger.info(f"Loaded index with {len(self.section_metadata)} sections")
            
        except Exception as e:
            self.logger.error(f"Error loading index: {str(e)}")
            raise
    
    def search_similar_sections(self, query: str, k: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for similar IPC sections using semantic similarity
        Returns sections with similarity scores above threshold
        """
        if self.index is None:
            raise ValueError("Index not loaded or built")
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search index
        distances, indices = self.index.search(query_embedding, k)
        
        # Format results with metadata and similarity scores
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.section_metadata):  # Valid index
                similarity_score = 1 / (1 + distance)  # Convert distance to similarity
                
                if similarity_score >= threshold:
                    result = self.section_metadata[idx].copy()
                    result['similarity_score'] = similarity_score
                    result['distance'] = distance
                    results.append(result)
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results


# Example usage for research paper
def demonstrate_vector_index():
    """Demonstration function for research paper"""
    
    # Initialize index manager
    index_manager = IPCVectorIndexManager()
    
    # Build index (would typically be done during setup)
    # index_manager.build_vector_index("dataset/ipc/ipc.json", "vector_index/")
    
    # Load pre-built index
    index_manager.load_index("vector_index/")
    
    # Example queries demonstrating semantic search capabilities
    test_queries = [
        "theft of mobile phone",
        "assault causing injury",
        "fraudulent financial transactions",
        "cyber crime involving data theft"
    ]
    
    results = {}
    for query in test_queries:
        similar_sections = index_manager.search_similar_sections(query, k=3)
        results[query] = similar_sections
    
    return results


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demonstration
    demo_results = demonstrate_vector_index()
    print("Vector Index Management Demonstration Complete")