import re
from typing import List, Dict
from legal_modules.ipc_module import ipc_module
from services.rag_service import rag_service
from utils.logging import log_info, log_error

class ChargePredictionService:
    def __init__(self):
        self.crime_keywords = {
            "theft": ["steal", "stole", "rob", "robbery", "snatch", "take"],
            "assault": ["hit", "beat", "strike", "attack", "harm", "injure"],
            "murder": ["kill", "murder", "death", "dead", "slay"],
            "rape": ["rape", "sexual assault", "molest", "harass"],
            "fraud": ["cheat", "deceive", "trick", "scam", "fake"],
            "trespass": ["enter", "trespass", "intrude", "break in"],
            "damage": ["break", "destroy", "damage", "ruin"],
            "kidnapping": ["kidnap", "abduct", "take away", "hold hostage"],
            "extortion": ["threaten", "demand", "blackmail", "coerce"]
        }
    
    def extract_crime_elements(self, scenario: str) -> Dict[str, bool]:
        """Extract crime elements from a scenario description"""
        elements = {
            "dishonest_intention": False,
            "threat": False,
            "force": False,
            "property_theft": False,
            "weapon_use": False,
            "group_participation": False,
            "trespass": False
        }
        
        scenario_lower = scenario.lower()
        
        # Check for dishonest intention keywords
        dishonest_words = ["dishonestly", "intentionally", "knowingly", "purposefully"]
        elements["dishonest_intention"] = any(word in scenario_lower for word in dishonest_words)
        
        # Check for threat keywords
        threat_words = ["threaten", "threat", "menace", "intimidate", "warn"]
        elements["threat"] = any(word in scenario_lower for word in threat_words)
        
        # Check for force keywords
        force_words = ["force", "violence", "violent", "physical", "push", "shove"]
        elements["force"] = any(word in scenario_lower for word in force_words)
        
        # Check for property theft keywords
        theft_words = ["steal", "stole", "rob", "robbery", "snatch", "take", "pilfer"]
        elements["property_theft"] = any(word in scenario_lower for word in theft_words)
        
        # Check for weapon use keywords
        weapon_words = ["knife", "gun", "weapon", "sword", "stick", "rod", "bat"]
        elements["weapon_use"] = any(word in scenario_lower for word in weapon_words)
        
        # Check for group participation keywords
        group_words = ["group", "gang", "together", "collective", "multiple people"]
        elements["group_participation"] = any(word in scenario_lower for word in group_words)
        
        # Check for trespass keywords
        trespass_words = ["trespass", "unauthorized entry", "break in", "intrude"]
        elements["trespass"] = any(word in scenario_lower for word in trespass_words)
        
        return elements
    
    def predict_charges(self, scenario: str) -> List[Dict]:
        """Predict possible IPC charges based on a scenario"""
        try:
            # Extract crime elements
            elements = self.extract_crime_elements(scenario)
            total_present_elements = sum(1 for present in elements.values() if present)
            
            # Use RAG service to find relevant sections
            rag_results = rag_service.search_similar_sections(scenario, top_k=10)
            
            # Score sections based on relevance
            scored_sections = []
            
            for result in rag_results:
                section = result["section"]
                score = result["score"]
                scenario_lower = scenario.lower()

                # Boost score based on matching elements
                boost = 0.0
                section_match_count = 0
                
                # Check if section dataset signals match the scenario
                searchable_terms = " ".join(
                    section.get("keywords", [])
                    + section.get("synonyms", [])
                    + section.get("legal_elements", [])
                    + section.get("vector_search_terms", [])
                ).lower()

                for element, present in elements.items():
                    if present and element.replace("_", " ") in searchable_terms:
                        boost += 0.1
                        section_match_count += 1

                for field in ("crime_category", "crime_subcategory", "severity_level"):
                    value = str(section.get(field, "")).replace("_", " ").lower()
                    if value and value in scenario_lower:
                        boost += 0.05
                        section_match_count += 1

                for scenario_example in section.get("example_scenarios", []):
                    if any(token in scenario_lower for token in scenario_example.lower().split()):
                        boost += 0.02
                        section_match_count += 1

                for training_example in section.get("scenario_training", []):
                    if any(token in scenario_lower for token in training_example.lower().split()):
                        boost += 0.02
                        section_match_count += 1

                # Additional boost for sections with high similarity
                final_score = score + boost
                
                scored_sections.append({
                    "section": section,
                    "score": final_score,
                    "raw_score": score,
                    "elements_matched": section_match_count,
                    "total_present_elements": total_present_elements
                })
            
            # Sort by score and take top results
            scored_sections.sort(key=lambda x: x["score"], reverse=True)
            top_sections = scored_sections[:5]  # Return top 5 predictions

            max_score = max((item["score"] for item in top_sections), default=0.0)
            min_score = min((item["score"] for item in top_sections), default=0.0)
            score_range = max_score - min_score
            
            # Format results
            predictions = []
            for rank, item in enumerate(top_sections):
                section = item["section"]
                related_sections = ipc_module.get_related_sections(section["section_number"])
                semantic_score = max(0.0, min(item["raw_score"], 1.0))
                relative_rank_score = 1.0 if score_range == 0 else (item["score"] - min_score) / score_range
                coverage_score = 0.0
                if item["total_present_elements"] > 0:
                    coverage_score = min(item["elements_matched"] / item["total_present_elements"], 1.0)

                rank_bonus = max(0.0, 0.12 - (rank * 0.02))
                calibrated_confidence = (
                    0.45 * semantic_score +
                    0.30 * relative_rank_score +
                    0.15 * coverage_score +
                    rank_bonus
                )
                calibrated_confidence = max(0.35, min(calibrated_confidence, 0.98))

                predictions.append({
                    "section": section["section_number"],
                    "title": section["title"],
                    "chapter": section.get("chapter"),
                    "description": section.get("description"),
                    "punishment": section["punishment"],
                    "confidence": round(calibrated_confidence, 3),
                    "citation": section["citation"],
                    "elements_matched": item["elements_matched"],
                    "crime_category": section.get("crime_category"),
                    "crime_subcategory": section.get("crime_subcategory"),
                    "severity_level": section.get("severity_level"),
                    "keywords": section.get("keywords", []),
                    "synonyms": section.get("synonyms", []),
                    "legal_elements": section.get("legal_elements", []),
                    "example_scenarios": section.get("example_scenarios", []),
                    "scenario_training": section.get("scenario_training", []),
                    "crime_type_mapping": section.get("crime_type_mapping", {}),
                    "vector_search_terms": section.get("vector_search_terms", []),
                    "court_judgment_links": section.get("court_judgment_links", []),
                    "related_sections": [
                        {
                            "section_number": related.get("section_number"),
                            "title": related.get("title")
                        }
                        for related in related_sections
                    ]
                })
            
            return predictions
            
        except Exception as e:
            log_error(f"Charge prediction failed: {str(e)}")
            return []

# Global charge prediction service instance
charge_prediction_service = ChargePredictionService()
