from typing import Dict, List

from services.charge_prediction import charge_prediction_service
from services.rag_service import rag_service


class IPCMapperAgent:
    def run(self, query: str, analysis: Dict) -> Dict:
        query_type = analysis.get("query_type", "scenario")

        if query_type == "question":
            results = rag_service.search_similar_sections(query, top_k=5)
            sections = []
            for item in results:
                section = item.get("section", {})
                sections.append(
                    {
                        "section": str(section.get("section_number")),
                        "title": section.get("title"),
                        "description": section.get("description"),
                        "punishment": section.get("punishment"),
                        "score": round(float(item.get("score", 0.0)), 3),
                        "source": "rag",
                        "section_data": section,
                    }
                )
        else:
            predictions = charge_prediction_service.predict_charges(query)
            sections = []
            for item in predictions:
                sections.append(
                    {
                        "section": str(item.get("section")),
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "punishment": item.get("punishment"),
                        "score": round(float(item.get("confidence", 0.0)), 3),
                        "source": "charge_prediction",
                        "section_data": {
                            "section_number": item.get("section"),
                            "title": item.get("title"),
                            "description": item.get("description"),
                            "punishment": item.get("punishment"),
                            "citation": item.get("citation"),
                            "severity_level": item.get("severity_level"),
                            "chapter": item.get("chapter"),
                            "keywords": item.get("keywords", []),
                            "related_sections": [
                                related.get("section_number")
                                for related in item.get("related_sections", [])
                                if related.get("section_number")
                            ],
                        },
                        "charge": item,
                    }
                )

        unique_sections: List[Dict] = []
        seen = set()
        for item in sections:
            section_number = item.get("section")
            if not section_number or section_number in seen:
                continue
            seen.add(section_number)
            unique_sections.append(item)

        return {
            "ipc_sections": unique_sections[:5],
            "matched_sections": [item["section_data"] for item in unique_sections[:5] if item.get("section_data")],
            "charges": [item.get("charge") for item in unique_sections if item.get("charge")][:5],
        }
