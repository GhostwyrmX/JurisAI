from typing import Dict, List


class ValidatorAgent:
    def run(self, payload: Dict, ipc_mapping: Dict) -> Dict:
        valid_sections = {
            str(item.get("section"))
            for item in ipc_mapping.get("ipc_sections", [])
            if item.get("section") and str(item.get("section")).isdigit()
        }

        filtered_sections: List[Dict] = []
        for item in payload.get("ipc_sections", []):
            section_number = str(item.get("section"))
            if section_number in valid_sections:
                filtered_sections.append(item)

        payload["ipc_sections"] = filtered_sections
        payload["sections_referenced"] = [item.get("section") for item in filtered_sections]
        payload["validation"] = {
            "ipc_only": True,
            "validated_sections": payload["sections_referenced"],
            "errors": [],
        }
        return payload
