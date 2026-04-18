from typing import Dict, List


class SeverityAgent:
    def run(self, query: str, ipc_mapping: Dict, analysis: Dict) -> Dict:
        sections: List[Dict] = ipc_mapping.get("ipc_sections", [])
        lower_query = query.lower()

        high_trigger_words = ["death", "killed", "murder", "rape", "acid", "gun", "knife", "kidnap"]
        medium_trigger_words = ["attack", "hurt", "injury", "threat", "extortion", "robbery", "fraud"]

        level = "LOW"
        rationale = []

        if any(word in lower_query for word in high_trigger_words):
            level = "HIGH"
            rationale.append("Query mentions a grave harm indicator such as death, sexual violence, kidnapping, or weapon use.")
        elif any(word in lower_query for word in medium_trigger_words):
            level = "MEDIUM"
            rationale.append("Query indicates coercion, bodily harm, or property crime with aggravating features.")

        mapped_high = []
        for item in sections:
            section_title = (item.get("title") or "").lower()
            section_description = (item.get("description") or "").lower()
            blob = f"{section_title} {section_description}"
            if any(token in blob for token in ["murder", "rape", "kidnapping", "grievous", "death"]):
                mapped_high.append(item.get("section"))

        if mapped_high:
            level = "HIGH"
            rationale.append(f"Mapped IPC sections include high-severity offences: {', '.join(mapped_high)}.")

        if not rationale:
            rationale.append("Mapped sections and described facts suggest a lower immediate harm profile.")

        urgency = {
            "HIGH": "Seek immediate police assistance and urgent medical or safety support if relevant.",
            "MEDIUM": "Document facts promptly and approach the police station with available records.",
            "LOW": "Preserve records and seek clarification before filing further legal steps.",
        }

        return {
            "level": level,
            "label": level,
            "rationale": rationale,
            "urgency_note": urgency[level],
        }
