import faiss
import numpy as np
import json
import os
import sys
import time
import hashlib

# Add parent directory to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, parent_dir)

from legal_modules.ipc_module import ipc_module
from utils.config import Config
from utils.logging import log_info, log_error
from cache.redis_cache import cache
from metrics.metrics_tracker import metrics_tracker

from sentence_transformers import SentenceTransformer

class RAGService:
    def __init__(self):
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.vector_index_path = Config.VECTOR_INDEX_PATH
        self.index = None
        self.sections = []
        self.load_or_build_index()
    
    def _create_document_for_embedding(self, section):
        """Create a document string from section data for embedding"""
        doc_parts = []

        chapter = section.get("chapter") or {}
        citation = section.get("citation") or {}
        punishment = section.get("punishment") or {}
        crime_type_mapping = section.get("crime_type_mapping") or {}

        if section.get("title"):
            doc_parts.append(f"Title: {section['title']}")

        if section.get("section_number"):
            doc_parts.append(f"Section Number: {section['section_number']}")

        if chapter.get("chapter_name"):
            doc_parts.append(f"Chapter: {chapter['chapter_name']}")

        if section.get("description"):
            doc_parts.append(f"Description: {section['description']}")
            
        if section.get("section_text"):
            doc_parts.append(f"Section Text: {section['section_text']}")
            
        if section.get("keywords") and isinstance(section.get("keywords"), list):
            doc_parts.append(f"Keywords: {', '.join(section['keywords'])}")

        if section.get("synonyms") and isinstance(section.get("synonyms"), list):
            doc_parts.append(f"Synonyms: {', '.join(section['synonyms'])}")

        if section.get("crime_category"):
            doc_parts.append(f"Crime Category: {section['crime_category']}")

        if section.get("crime_subcategory"):
            doc_parts.append(f"Crime Subcategory: {section['crime_subcategory']}")

        if section.get("severity_level"):
            doc_parts.append(f"Severity Level: {section['severity_level']}")

        if section.get("legal_elements") and isinstance(section.get("legal_elements"), list):
            doc_parts.append(f"Legal Elements: {', '.join(section['legal_elements'])}")
            
        if section.get("example_scenarios") and isinstance(section.get("example_scenarios"), list):
            doc_parts.append(f"Example Scenarios: {' '.join(section['example_scenarios'])}")

        if section.get("scenario_training") and isinstance(section.get("scenario_training"), list):
            doc_parts.append(f"Scenario Training: {' '.join(section['scenario_training'])}")

        if section.get("vector_search_terms") and isinstance(section.get("vector_search_terms"), list):
            doc_parts.append(f"Search Terms: {', '.join(section['vector_search_terms'])}")

        if isinstance(section.get("related_sections"), list) and section.get("related_sections"):
            doc_parts.append(f"Related Sections: {', '.join(section['related_sections'])}")

        if crime_type_mapping:
            mapping_parts = [
                f"{key.replace('_', ' ').title()}: {value}"
                for key, value in crime_type_mapping.items()
                if value and value != "not_applicable"
            ]
            if mapping_parts:
                doc_parts.append(f"Crime Type Mapping: {', '.join(mapping_parts)}")

        punishment_parts = [
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in punishment.items()
            if value and value != "not_applicable"
        ]
        if punishment_parts:
            doc_parts.append(f"Punishment: {', '.join(punishment_parts)}")

        if citation.get("law") and citation.get("section"):
            doc_parts.append(f"Citation: {citation['law']} Section {citation['section']}")

        if citation.get("verified") is not None:
            doc_parts.append(f"Verified Citation: {citation['verified']}")

        if section.get("court_judgment_links") and isinstance(section.get("court_judgment_links"), list):
            doc_parts.append(f"Court Judgment Links: {' '.join(str(item) for item in section['court_judgment_links'])}")

        return " ".join(doc_parts)
    
    def build_vector_index(self):
        """Build FAISS index from IPC sections"""
        try:
            log_info("Building vector index from IPC sections")
            print("Building vector index from IPC sections")
            
            # Get all sections
            self.sections = ipc_module.get_all_sections()
            print(f"Loaded {len(self.sections)} sections")
            
            # Create documents for embedding
            documents = []
            print(f"Creating documents for {len(self.sections)} sections...")
            for i, section in enumerate(self.sections):
                doc = self._create_document_for_embedding(section)
                documents.append(doc)
                if (i + 1) % 50 == 0:
                    print(f"Created documents for {i + 1}/{len(self.sections)} sections...")
            
            # Generate embeddings
            log_info(f"Generating embeddings for {len(documents)} documents")
            print(f"Generating embeddings for {len(documents)} documents...")
            embeddings = self.embedding_model.encode(documents)
            print("Embeddings generated successfully")
            
            # Build FAISS index
            print("Building FAISS index...")
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            print("Adding embeddings to index...")
            self.index.add(embeddings.astype(np.float32))
            
            # Save index
            index_path = os.path.join(os.getcwd(), self.vector_index_path)
            print(f"Saving index to {index_path}...")
            faiss.write_index(self.index, index_path)
            
            # Save metadata
            meta_path = index_path + ".meta"
            print(f"Saving metadata to {meta_path}...")
            metadata = {
                "dataset_hash": "computed_hash",  # In practice, compute actual hash
                "embedding_model": Config.EMBEDDING_MODEL,
                "build_timestamp": time.time(),
                "section_count": len(self.sections)
            }
            
            with open(meta_path, "w") as f:
                json.dump(metadata, f)
                
            log_info(f"Vector index built and saved to {index_path}")
            print(f"Vector index built and saved to {index_path}")
            
        except Exception as e:
            log_error(f"Failed to build vector index: {str(e)}")
            print(f"Failed to build vector index: {str(e)}")
            raise
            raise
    
    def load_or_build_index(self):
        """Load existing index or build a new one"""
        try:
            index_path = os.path.join(os.getcwd(), self.vector_index_path)
            
            if os.path.exists(index_path):
                # Load existing index
                self.index = faiss.read_index(index_path)
                self.sections = ipc_module.get_all_sections()
                log_info(f"Loaded existing vector index from {index_path}")
            else:
                # Build new index
                self.build_vector_index()
                
        except Exception as e:
            log_error(f"Failed to load vector index: {str(e)}")
            # Try to build a new one
            self.build_vector_index()
    
    def search_similar_sections(self, query, top_k=5):
        """Search for similar sections using vector similarity"""
        try:
            # Track vector search
            metrics_tracker.record_vector_search()
            
            # Check cache first
            cache_key = f"embedding_{hashlib.sha256(query.encode('utf-8')).hexdigest()}"
            cached_result = cache.get(cache_key)
            if cached_result:
                metrics_tracker.record_cache_hit()
                return cached_result
            else:
                metrics_tracker.record_cache_miss()
            
            # Check if query contains a specific section number
            import re
            section_match = re.search(r'section\s+(\d+)', query.lower())
            if section_match:
                section_number = section_match.group(1)
                # Try to find the exact section
                for section in self.sections:
                    if str(section.get('section_number')) == section_number:
                        metrics_tracker.record_cache_hit()  # Count as cache hit for direct lookup
                        return [{
                            "section": section,
                            "score": 1.0  # Perfect match
                        }]
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search index
            scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)
            
            # Get sections by indices
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and i < len(self.sections):  # Check if valid index
                    section = self.sections[idx]
                    results.append({
                        "section": section,
                        "score": float(scores[0][i])
                    })
            
            # Cache results
            cache.set(cache_key, results, ttl=86400)  # 24 hours
            
            return results
            
        except Exception as e:
            log_error(f"Vector search failed: {str(e)}")
            return []

# Global RAG service instance
rag_service = RAGService()
