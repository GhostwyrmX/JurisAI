from typing import Dict, List


class FIRAgent:
    def run(self, query: str, analysis: Dict, ipc_mapping: Dict) -> Dict:
        sections = [item.get("section") for item in ipc_mapping.get("ipc_sections", []) if item.get("section")]
        cited_sections = ", ".join(sections) if sections else "to be determined after police review"

        complaint_lines: List[str] = [
            "To,",
            "The Station House Officer,",
            "Concerned Police Station,",
            "",
            "Subject: Complaint regarding the incident described below",
            "",
            "Respected Sir/Madam,",
            "",
            "I respectfully submit that the following incident requires registration and investigation under the Indian Penal Code.",
            "",
            f"Incident summary: {analysis.get('normalized_query', query).strip()}",
            f"Possible IPC sections for consideration: {cited_sections}.",
            "",
            "I request that my complaint be recorded, the relevant facts be verified, and necessary action be taken in accordance with law.",
            "",
            "I am ready to provide supporting documents, witness details, and any additional clarification required.",
            "",
            "Name:",
            "Address:",
            "Phone:",
            "Date:",
            "Signature:",
        ]

        return {
            "complaint_draft": "\n".join(complaint_lines),
            "complaint_title": "Draft FIR / Complaint",
        }
