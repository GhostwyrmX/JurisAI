from typing import Dict, List


class ActionAgent:
    def run(self, analysis: Dict, severity: Dict, ipc_mapping: Dict, evidence: Dict) -> Dict:
        steps: List[Dict] = [
            {
                "title": "Stabilize the situation",
                "detail": severity.get("urgency_note", "Ensure immediate safety and basic documentation."),
            },
            {
                "title": "Organize the facts",
                "detail": "Prepare a timeline with who, what, when, where, and how the event occurred.",
            },
            {
                "title": "Collect core evidence",
                "detail": evidence.get("preservation_note", "Keep documents and digital records intact."),
            },
            {
                "title": "Approach the police station",
                "detail": "Present the incident summary and the mapped IPC sections as possible references, not as final legal conclusions.",
            },
            {
                "title": "Retain acknowledgement",
                "detail": "Keep diary number, complaint copy, or receipt of submission for follow-up.",
            },
        ]

        if analysis.get("query_type") == "question":
            steps = steps[1:]

        quick_tips = [
            "Keep your description factual and chronological.",
            "Mention exact dates, times, and locations where known.",
            "Separate what you directly saw from what others told you.",
        ]

        donts = [
            "Do not add facts you cannot verify.",
            "Do not cite non-IPC laws in this IPC-only workflow.",
            "Do not alter screenshots, photos, or original records.",
        ]

        return {
            "steps": steps,
            "tips": quick_tips,
            "donts": donts,
        }
