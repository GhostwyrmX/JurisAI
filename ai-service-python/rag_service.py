"""
RAG Service Implementation for Legal Information Retrieval
Research paper implementation with sentence transformer embeddings and FAISS
"""

from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging
from datetime import datetime
import json
from .vector_index_management import IPCVectorIndexManager


class RAGService:
    """
    Retrieval-Augmented Generation Service for legal context-based response generation
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 index_manager: Optional[IPCVectorIndexManager] = None):
        
        self.embedding_model = SentenceTransformer(model_name)
        self.index_manager = index_manager or IPCVectorIndexManager(model_name)
        self.logger = logging.getLogger(__name__)
        self.cache = {}  # Simple in-memory cache for frequent queries
        
    def initialize_service(self, index_path: str) -> None:
        """Initialize RAG service with pre-built index"""
        try:
            self.index_manager.load_index(index_path)
            self.logger.info("RAG service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG service: {str(e)}")
            raise
    
    def retrieve_legal_context(self, query: str, max_results: int = 5, 
                             similarity_threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Retrieve relevant legal context for a query using semantic search
        """
        # Check cache first
        cache_key = f"{query}_{max_results}_{similarity_threshold}"
        if cache_key in self.cache:
            cached_time, cached_results = self.cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < 300:  # 5 minute cache
                self.logger.debug("Returning cached results")
                return cached_results
        
        try:
            # Perform semantic search
            results = self.index_manager.search_similar_sections(
                query, k=max_results, threshold=similarity_threshold
            )
            
            # Cache results
            self.cache[cache_key] = (datetime.now(), results)
            
            self.logger.info(f"Retrieved {len(results)} relevant sections for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving legal context: {str(e)}")
            return []
    
    def format_retrieved_context(self, retrieved_sections: List[Dict[str, Any]]) -> str:
        """
        Format retrieved sections into a coherent context string for LLM prompting
        """
        if not retrieved_sections:
            return "No relevant legal provisions found."
        
        context_parts = ["RELEVANT LEGAL PROVISIONS:"]
        
        for i, section in enumerate(retrieved_sections, 1):
            context_parts.append(
                f"{i}. IPC Section {section.get('section_number', 'N/A')}: "
                f"{section.get('title', 'No title')} "
                f"(Similarity: {section.get('similarity_score', 0):.3f})\n"
                f"Description: {section.get('description', 'No description')}\n"
                f"Legal Elements: {section.get('legal_elements', 'No elements specified')}\n"
                f"Punishment: {section.get('punishment', 'No punishment specified')}\n"
                f"Category: {section.get('category', 'Uncategorized')} | "
                f"Severity: {section.get('severity', 'Not specified')}"
            )
        
        return "\n\n".join(context_parts)
    
    def generate_grounded_response(self, query: str, retrieved_context: str, 
                                 llm_service: Any, max_length: int = 512) -> Dict[str, Any]:
        """
        Generate response grounded in retrieved legal context with proper citation
        """
        prompt = self._construct_legal_prompt(query, retrieved_context)
        
        try:
            # Use LLM service to generate response
            response = llm_service.generate_response(
                prompt, 
                max_length=max_length,
                temperature=0.1,  # Low temperature for factual accuracy
                stop_sequences=["\n\n", "END_OF_RESPONSE"]
            )
            
            # Parse and validate response
            parsed_response = self._parse_llm_response(response, retrieved_context)
            
            return {
                'response_text': parsed_response,
                'retrieved_sections': retrieved_context,
                'timestamp': datetime.now().isoformat(),
                'query': query
            }
            
        except Exception as e:
            self.logger.error(f"Error generating grounded response: {str(e)}")
            return {
                'response_text': f"I apologize, but I encountered an error processing your legal query. Please try again or consult a legal professional for specific advice. Error: {str(e)}",
                'retrieved_sections': retrieved_context,
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'error': True
            }
    
    def _construct_legal_prompt(self, query: str, context: str) -> str:
        """Construct structured prompt for legal response generation"""
        return f"""
You are a legal information assistant specializing in Indian Penal Code (IPC) provisions. 
Your task is to provide accurate, factual information based strictly on the retrieved legal context.

CONTEXT:
{context}

QUERY: {query}

INSTRUCTIONS:
1. Base your response ONLY on the provided legal provisions
2. Cite specific IPC sections when referencing laws
3. If multiple sections are relevant, explain how they relate
4. Be precise about legal elements and requirements
5. Clearly state if the query doesn't match any provisions
6. Do not speculate beyond the provided context
7. Use formal legal language but make it understandable
8. End your response with "END_OF_RESPONSE"

RESPONSE:
"""
    
    def _parse_llm_response(self, response: str, context: str) -> str:
        """Parse and validate LLM response for legal accuracy"""
        # Basic validation - ensure response contains citations if context exists
        if context != "No relevant legal provisions found." and "IPC Section" not in response:
            self.logger.warning("LLM response missing expected IPC citations")
            
        # Remove stop sequence if present
        if "END_OF_RESPONSE" in response:
            response = response.split("END_OF_RESPONSE")[0].strip()
            
        return response
    
    def process_legal_query(self, query: str, llm_service: Any, 
                          max_retrieval: int = 5, similarity_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Complete RAG pipeline for legal query processing
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Retrieve relevant legal context
            retrieved_sections = self.retrieve_legal_context(
                query, max_results=max_retrieval, similarity_threshold=similarity_threshold
            )
            
            # Step 2: Format context for LLM
            formatted_context = self.format_retrieved_context(retrieved_sections)
            
            # Step 3: Generate grounded response
            response = self.generate_grounded_response(query, formatted_context, llm_service)
            
            # Add performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            response['processing_time_seconds'] = processing_time
            response['retrieved_count'] = len(retrieved_sections)
            
            self.logger.info(
                f"Processed query in {processing_time:.2f}s, "
                f"retrieved {len(retrieved_sections)} sections"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in RAG pipeline: {str(e)}")
            return {
                'error': True,
                'error_message': str(e),
                'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }


# Example usage for research paper
def demonstrate_rag_service():
    """Demonstration function for research paper"""
    
    # Initialize RAG service
    rag_service = RAGService()
    rag_service.initialize_service("vector_index/")
    
    # Example legal queries
    test_queries = [
        "What is the punishment for theft of a mobile phone?",
        "What constitutes assault under IPC?",
        "Explain the legal elements required for fraud"
    ]
    
    results = {}
    
    # Mock LLM service for demonstration
    class MockLLMService:
        def generate_response(self, prompt, **kwargs):
            return "Based on IPC Section 378, theft involves dishonestly taking movable property. Punishment may include imprisonment up to 3 years. END_OF_RESPONSE"
    
    llm_service = MockLLMService()
    
    for query in test_queries:
        result = rag_service.process_legal_query(query, llm_service)
        results[query] = result
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_results = demonstrate_rag_service()
    print("RAG Service Demonstration Complete")