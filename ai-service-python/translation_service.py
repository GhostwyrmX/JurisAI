"""
Multilingual Translation Service for Legal Terminology
Research implementation with legal domain optimization
"""

from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import re
from sentence_transformers import SentenceTransformer, util
import numpy as np


class TranslationService:
    """
    Translation service optimized for legal terminology with domain-specific handling
    """
    
    def __init__(self, 
                 model_name: str = "Helsinki-NLP/opus-mt-en-hi",  # English to Hindi
                 legal_embedding_model: str = "all-MiniLM-L6-v2"):
        
        self.logger = logging.getLogger(__name__)
        
        # Load translation model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.translator = self._load_translation_model(model_name)
        
        # Load legal embedding model for terminology validation
        self.legal_embedder = SentenceTransformer(legal_embedding_model)
        
        # Legal terminology dictionaries (simplified examples)
        self.legal_terminology = {
            'en': {
                'theft': 'theft',
                'assault': 'assault', 
                'fraud': 'fraud',
                'murder': 'murder',
                'rape': 'rape',
                'kidnapping': 'kidnapping',
                'property': 'property',
                'intent': 'intent',
                'punishment': 'punishment',
                'section': 'section',
                'IPC': 'Indian Penal Code'
            },
            'hi': {
                'theft': 'चोरी',
                'assault': 'हमला',
                'fraud': 'धोखाधड़ी', 
                'murder': 'हत्या',
                'rape': 'बलात्कार',
                'kidnapping': 'अपहरण',
                'property': 'संपत्ति',
                'intent': 'इरादा',
                'punishment': 'सजा',
                'section': 'धारा',
                'IPC': 'भारतीय दंड संहिता'
            }
        }
        
        # Language support configuration
        self.supported_languages = {
            'hi': 'Hindi',
            'en': 'English',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'ml': 'Malayalam'
        }
        
        # Legal domain patterns for special handling
        self.legal_patterns = {
            'ipc_section': r'IPC Section \d+[A-Z]*',
            'legal_citation': r'\b\d+ [A-Z\.]+ \d+\b',
            'legal_terms': r'\b(theft|assault|fraud|murder|rape|kidnapping)\b'
        }
        
        self.logger.info(f"Translation service initialized for device: {self.device}")
    
    def _load_translation_model(self, model_name: str):
        """Load translation model with error handling"""
        try:
            # Use pipeline for easier translation
            return pipeline(
                "translation",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,
                max_length=512
            )
        except Exception as e:
            self.logger.error(f"Failed to load translation model: {str(e)}")
            # Fallback to a simpler approach
            return None
    
    def translate_legal_text(self, text: str, target_lang: str, 
                           source_lang: str = 'en') -> Dict[str, Any]:
        """
        Translate legal text with terminology preservation and validation
        """
        start_time = datetime.now()
        
        if target_lang not in self.supported_languages:
            return {
                'error': f"Unsupported target language: {target_lang}",
                'supported_languages': list(self.supported_languages.keys())
            }
        
        try:
            # Step 1: Pre-process text to preserve legal elements
            preserved_elements = self._extract_legal_elements(text)
            processed_text = self._preserve_legal_terms(text, preserved_elements)
            
            # Step 2: Perform translation
            if self.translator and source_lang == 'en' and target_lang == 'hi':
                # Use trained model for EN->HI
                translation_result = self.translator(processed_text)
                translated_text = translation_result[0]['translation_text']
            else:
                # Fallback: terminology replacement for other languages
                translated_text = self._fallback_translation(processed_text, target_lang)
            
            # Step 3: Restore preserved legal elements
            final_translation = self._restore_legal_terms(translated_text, preserved_elements)
            
            # Step 4: Validate translation quality
            validation_result = self._validate_translation(text, final_translation, target_lang)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'translated_text': final_translation,
                'source_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'processing_time': processing_time,
                'preserved_elements': preserved_elements,
                'validation_score': validation_result['score'],
                'validation_issues': validation_result['issues'],
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Translation error: {str(e)}")
            return {
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'success': False
            }
    
    def _extract_legal_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract legal elements that should be preserved during translation"""
        elements = {
            'ipc_sections': [],
            'citations': [],
            'legal_terms': []
        }
        
        # Extract IPC sections
        ipc_matches = re.findall(self.legal_patterns['ipc_section'], text, re.IGNORECASE)
        elements['ipc_sections'] = list(set(ipc_matches))
        
        # Extract legal citations
        citation_matches = re.findall(self.legal_patterns['legal_citation'], text)
        elements['citations'] = list(set(citation_matches))
        
        # Extract key legal terms
        term_matches = re.findall(self.legal_patterns['legal_terms'], text, re.IGNORECASE)
        elements['legal_terms'] = list(set(term_matches))
        
        return elements
    
    def _preserve_legal_terms(self, text: str, elements: Dict[str, List[str]]) -> str:
        """Replace legal terms with placeholders for preservation"""
        processed_text = text
        
        # Replace IPC sections
        for i, section in enumerate(elements['ipc_sections']):
            placeholder = f"IPC_SECTION_{i}"
            processed_text = processed_text.replace(section, placeholder)
        
        # Replace citations
        for i, citation in enumerate(elements['citations']):
            placeholder = f"CITATION_{i}"
            processed_text = processed_text.replace(citation, placeholder)
        
        # Replace legal terms (more careful replacement)
        for i, term in enumerate(elements['legal_terms']):
            placeholder = f"LEGAL_TERM_{i}"
            # Use word boundaries to avoid partial matches
            processed_text = re.sub(r'\b' + re.escape(term) + r'\b', placeholder, processed_text)
        
        return processed_text
    
    def _restore_legal_terms(self, translated_text: str, elements: Dict[str, List[str]]) -> str:
        """Restore preserved legal elements after translation"""
        restored_text = translated_text
        
        # Restore IPC sections
        for i, section in enumerate(elements['ipc_sections']):
            placeholder = f"IPC_SECTION_{i}"
            restored_text = restored_text.replace(placeholder, section)
        
        # Restore citations
        for i, citation in enumerate(elements['citations']):
            placeholder = f"CITATION_{i}"
            restored_text = restored_text.replace(placeholder, citation)
        
        # Restore legal terms
        for i, term in enumerate(elements['legal_terms']):
            placeholder = f"LEGAL_TERM_{i}"
            restored_text = restored_text.replace(placeholder, term)
        
        return restored_text
    
    def _fallback_translation(self, text: str, target_lang: str) -> str:
        """Fallback translation using terminology replacement"""
        # Simple word-by-word replacement for demonstration
        # In production, this would use proper translation APIs
        
        if target_lang == 'hi' and hasattr(self, 'legal_terminology'):
            translated_text = text
            for en_term, hi_term in self.legal_terminology['hi'].items():
                # Replace whole words only
                translated_text = re.sub(
                    r'\b' + re.escape(en_term) + r'\b', 
                    hi_term, 
                    translated_text, 
                    flags=re.IGNORECASE
                )
            return translated_text
        
        # Return original text for unsupported languages
        return text
    
    def _validate_translation(self, source_text: str, translated_text: str, 
                            target_lang: str) -> Dict[str, Any]:
        """Validate translation quality using semantic similarity"""
        try:
            # Generate embeddings for comparison
            source_embedding = self.legal_embedder.encode([source_text], convert_to_numpy=True)
            translated_embedding = self.legal_embedder.encode([translated_text], convert_to_numpy=True)
            
            # Calculate cosine similarity
            similarity = util.pytorch_cos_sim(source_embedding, translated_embedding).item()
            
            # Check for terminology preservation
            terminology_issues = self._check_terminology_preservation(source_text, translated_text)
            
            return {
                'score': similarity,
                'issues': terminology_issues,
                'quality': 'GOOD' if similarity > 0.7 else 'FAIR' if similarity > 0.5 else 'POOR'
            }
            
        except Exception as e:
            self.logger.warning(f"Translation validation failed: {str(e)}")
            return {'score': 0.0, 'issues': ['Validation error'], 'quality': 'UNKNOWN'}
    
    def _check_terminology_preservation(self, source: str, translation: str) -> List[str]:
        """Check if key legal terminology was properly preserved"""
        issues = []
        
        # Check for IPC sections
        source_sections = re.findall(self.legal_patterns['ipc_section'], source, re.IGNORECASE)
        trans_sections = re.findall(self.legal_patterns['ipc_section'], translation, re.IGNORECASE)
        
        if set(source_sections) != set(trans_sections):
            issues.append("IPC section preservation issue")
        
        # Check key legal terms (simplified)
        source_terms = re.findall(self.legal_patterns['legal_terms'], source, re.IGNORECASE)
        
        for term in source_terms:
            if term.lower() not in translation.lower():
                issues.append(f"Legal term '{term}' not preserved")
        
        return issues
    
    def batch_translate(self, texts: List[str], target_lang: str, 
                      source_lang: str = 'en') -> List[Dict[str, Any]]:
        """Translate multiple texts with batch processing"""
        results = []
        
        for text in texts:
            result = self.translate_legal_text(text, target_lang, source_lang)
            results.append(result)
        
        return results
    
    def get_translation_quality_metrics(self) -> Dict[str, Any]:
        """Get service performance and quality metrics"""
        return {
            'supported_languages': list(self.supported_languages.keys()),
            'device': str(self.device),
            'model_loaded': self.translator is not None,
            'legal_terminology_size': len(self.legal_terminology['en']),
            'timestamp': datetime.now().isoformat()
        }


# Example usage for research paper
def demonstrate_translation_service():
    """Demonstration function for research paper"""
    
    service = TranslationService()
    
    # Example legal texts for translation
    legal_texts = [
        "IPC Section 378 defines theft as dishonestly taking movable property.",
        "The punishment for assault under IPC Section 323 may include imprisonment.",
        "Fraud under Section 420 requires deception and wrongful gain.",
        "Murder under Section 302 carries life imprisonment or death penalty."
    ]
    
    results = {}
    
    for text in legal_texts:
        translation_result = service.translate_legal_text(text, 'hi')
        results[text] = translation_result
    
    # Get service metrics
    metrics = service.get_translation_quality_metrics()
    
    return {
        'translation_results': results,
        'service_metrics': metrics
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_results = demonstrate_translation_service()
    print("Translation Service Demonstration Complete")