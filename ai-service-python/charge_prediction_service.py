"""
Charge Prediction Service with Confidence Scoring
Research implementation for IPC scenario analysis
"""

from typing import List, Dict, Any, Tuple, Optional
import re
import numpy as np
from sentence_transformers import SentenceTransformer, util
import logging
from datetime import datetime
from .vector_index_management import IPCVectorIndexManager


class ChargePredictionService:
    """
    Service for predicting applicable IPC charges from scenario descriptions
    with hybrid rule-based and semantic similarity approach
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.similarity_model = SentenceTransformer(model_name)
        self.index_manager = IPCVectorIndexManager(model_name)
        self.logger = logging.getLogger(__name__)
        
        # Predefined crime keyword dictionaries for rule-based extraction
        self.crime_keywords = {
            'theft': ['steal', 'theft', 'rob', 'take without permission', 'snatch', 'pilfer'],
            'assault': ['assault', 'attack', 'hit', 'beat', 'violence', 'harm', 'injure'],
            'fraud': ['fraud', 'cheat', 'deceive', 'false pretense', 'swindle', 'defraud'],
            'cybercrime': ['hack', 'cyber', 'computer', 'data theft', 'online fraud', 'phishing'],
            'murder': ['kill', 'murder', 'homicide', 'cause death', 'eliminate'],
            'rape': ['rape', 'sexual assault', 'molest', 'abuse', 'violate'],
            'kidnapping': ['kidnap', 'abduct', 'take hostage', 'capture', 'hold against will']
        }
        
        # Legal element extraction patterns
        self.element_patterns = {
            'intent': [r'intent to', r'with the purpose', r'aiming to', r'planned to'],
            'property': [r'property', r'money', r'valuables', r'assets', r'belongings'],
            'violence': [r'force', r'violence', r'physical harm', r'assault', r'attack'],
            'deception': [r'deceive', r'false', r'misrepresent', r'pretend', r'fake']
        }
        
        # IPC section to crime type mapping (simplified)
        self.ipc_crime_mapping = {
            '378': 'theft',
            '379': 'theft',
            '323': 'assault',
            '324': 'assault',
            '420': 'fraud',
            '375': 'rape',
            '376': 'rape',
            '302': 'murder',
            '363': 'kidnapping'
        }
    
    def extract_crime_keywords(self, scenario: str) -> Dict[str, float]:
        """
        Extract crime-related keywords from scenario description
        Returns dictionary with crime types and confidence scores
        """
        scenario_lower = scenario.lower()
        keyword_scores = {}
        
        for crime_type, keywords in self.crime_keywords.items():
            matches = 0
            for keyword in keywords:
                if keyword in scenario_lower:
                    matches += 1
            
            # Calculate confidence based on keyword matches
            if matches > 0:
                confidence = min(1.0, matches / len(keywords) * 2)  # Scale to 0-1
                keyword_scores[crime_type] = confidence
        
        return keyword_scores
    
    def extract_legal_elements(self, scenario: str) -> Dict[str, List[str]]:
        """
        Extract potential legal elements from scenario description
        """
        elements_found = {}
        scenario_lower = scenario.lower()
        
        for element_type, patterns in self.element_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, scenario_lower)
                matches.extend(found)
            
            if matches:
                elements_found[element_type] = list(set(matches))
        
        return elements_found
    
    def calculate_semantic_similarity(self, scenario: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Calculate semantic similarity between scenario and IPC sections
        """
        try:
            # Use the index manager for semantic search
            similar_sections = self.index_manager.search_similar_sections(
                scenario, k=max_results, threshold=0.4  # Lower threshold for broader search
            )
            
            return similar_sections
            
        except Exception as e:
            self.logger.error(f"Error in semantic similarity calculation: {str(e)}")
            return []
    
    def predict_charges(self, scenario: str, max_predictions: int = 5) -> List[Dict[str, Any]]:
        """
        Predict applicable IPC charges with confidence scoring
        Hybrid approach combining keyword matching and semantic similarity
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Keyword-based extraction
            keyword_scores = self.extract_crime_keywords(scenario)
            
            # Step 2: Legal element extraction
            legal_elements = self.extract_legal_elements(scenario)
            
            # Step 3: Semantic similarity search
            similar_sections = self.calculate_semantic_similarity(scenario)
            
            # Step 4: Combine evidence for confidence scoring
            predictions = self._combine_evidence(
                keyword_scores, similar_sections, legal_elements
            )
            
            # Step 5: Sort and limit predictions
            sorted_predictions = sorted(
                predictions, key=lambda x: x['confidence_score'], reverse=True
            )[:max_predictions]
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                f"Charge prediction completed in {processing_time:.2f}s. "
                f"Found {len(sorted_predictions)} potential charges for scenario"
            )
            
            return {
                'predictions': sorted_predictions,
                'processing_time': processing_time,
                'scenario_elements': legal_elements,
                'keyword_matches': keyword_scores,
                'total_sections_considered': len(similar_sections)
            }
            
        except Exception as e:
            self.logger.error(f"Error in charge prediction: {str(e)}")
            return {
                'predictions': [],
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def _combine_evidence(self, keyword_scores: Dict[str, float], 
                         similar_sections: List[Dict[str, Any]],
                         legal_elements: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Combine multiple evidence sources for confidence scoring
        """
        predictions = {}
        
        # Process semantic similarity results
        for section in similar_sections:
            section_number = section.get('section_number')
            similarity_score = section.get('similarity_score', 0)
            
            # Get crime type from mapping
            crime_type = self.ipc_crime_mapping.get(section_number, 'unknown')
            
            # Base confidence on semantic similarity
            base_confidence = similarity_score
            
            # Boost confidence if keywords match crime type
            keyword_boost = keyword_scores.get(crime_type, 0) * 0.3
            
            # Additional boost for relevant legal elements
            element_boost = self._calculate_element_boost(crime_type, legal_elements) * 0.2
            
            # Calculate final confidence
            final_confidence = min(1.0, base_confidence + keyword_boost + element_boost)
            
            if section_number not in predictions or final_confidence > predictions[section_number]['confidence_score']:
                predictions[section_number] = {
                    'section_number': section_number,
                    'title': section.get('title'),
                    'confidence_score': final_confidence,
                    'similarity_score': similarity_score,
                    'keyword_confidence': keyword_scores.get(crime_type, 0),
                    'crime_type': crime_type,
                    'legal_elements': legal_elements,
                    'description': section.get('description', '')[:200] + '...'  # Truncate
                }
        
        return list(predictions.values())
    
    def _calculate_element_boost(self, crime_type: str, legal_elements: Dict[str, List[str]]) -> float:
        """
        Calculate confidence boost based on relevant legal elements
        """
        element_importance = {
            'theft': ['intent', 'property'],
            'assault': ['violence', 'intent'],
            'fraud': ['deception', 'property'],
            'murder': ['intent', 'violence'],
            'rape': ['violence', 'intent'],
            'kidnapping': ['intent', 'violence']
        }
        
        if crime_type not in element_importance:
            return 0.0
        
        important_elements = element_importance[crime_type]
        matches = sum(1 for element in important_elements if element in legal_elements)
        
        return matches / len(important_elements)
    
    def get_confidence_level(self, confidence_score: float) -> str:
        """
        Convert numerical confidence score to descriptive level
        """
        if confidence_score >= 0.8:
            return "HIGH"
        elif confidence_score >= 0.6:
            return "MEDIUM"
        elif confidence_score >= 0.4:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def format_predictions(self, prediction_results: Dict[str, Any]) -> str:
        """
        Format prediction results for user presentation
        """
        if not prediction_results.get('predictions'):
            return "No applicable charges identified with sufficient confidence."
        
        output = ["PREDICTED IPC CHARGES:"]
        
        for i, prediction in enumerate(prediction_results['predictions'], 1):
            confidence_level = self.get_confidence_level(prediction['confidence_score'])
            
            output.append(
                f"{i}. IPC Section {prediction['section_number']}: {prediction['title']}\n"
                f"   Confidence: {confidence_level} ({prediction['confidence_score']:.3f})\n"
                f"   Crime Type: {prediction['crime_type'].upper()}\n"
                f"   Similarity: {prediction['similarity_score']:.3f}\n"
                f"   Keyword Match: {prediction['keyword_confidence']:.3f}\n"
                f"   Description: {prediction['description']}"
            )
        
        # Add summary information
        output.append(f"\nProcessing Time: {prediction_results['processing_time']:.2f}s")
        output.append(f"Sections Considered: {prediction_results['total_sections_considered']}")
        
        return "\n\n".join(output)


# Example usage for research paper
def demonstrate_charge_prediction():
    """Demonstration function for research paper"""
    
    service = ChargePredictionService()
    
    # Example scenarios
    test_scenarios = [
        "A person took my mobile phone without permission while I was distracted",
        "Someone attacked me with a knife and caused injuries",
        "A company deceived me into investing in a fake business opportunity",
        "Unknown persons hacked into my computer and stole personal data"
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        prediction = service.predict_charges(scenario)
        formatted_output = service.format_predictions(prediction)
        results[scenario] = {
            'raw_prediction': prediction,
            'formatted_output': formatted_output
        }
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_results = demonstrate_charge_prediction()
    print("Charge Prediction Service Demonstration Complete")