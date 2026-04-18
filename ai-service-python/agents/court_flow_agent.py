from typing import Dict, List


class CourtFlowAgent:
    def run(self, severity: Dict, ipc_mapping: Dict) -> Dict:
        sections = [item.get("section") for item in ipc_mapping.get("ipc_sections", []) if item.get("section")]
        level = severity.get("level", "LOW")

        timeline = {
            "HIGH": "Immediate complaint and investigation stage, with court-linked steps possibly starting within days to weeks depending on arrest and remand.",
            "MEDIUM": "Investigation and filing stages commonly unfold over weeks, followed by charge framing and evidence stages.",
            "LOW": "Early stages may move slower and often depend on document collection, complaint follow-up, and police verification.",
        }

        outcomes = {
            "HIGH": ["Investigation with urgent evidence collection", "Possible arrest or custodial process", "Charge sheet and trial preparation"],
            "MEDIUM": ["Police inquiry and witness statements", "Charge sheet or closure depending on evidence", "Trial or discharge-related hearings"],
            "LOW": ["Complaint review", "Fact verification", "Possible summons or closure if evidence is weak"],
        }

        user_involvement = [
            "Provide a consistent chronology whenever asked by police or court.",
            "Attend when called for statement, identification, or hearing-related steps.",
            "Preserve originals of every document submitted.",
        ]

        stages: List[Dict] = [
            {"stage": "Complaint / FIR", "detail": "Police receives the complaint and assesses the IPC allegations."},
            {"stage": "Investigation", "detail": "Statements, documents, site facts, and seizure records are collected."},
            {"stage": "Charge Sheet / Final Report", "detail": "Police files its conclusions before the competent court."},
            {"stage": "Cognizance and Hearing", "detail": "Court examines the report and begins the trial pathway where applicable."},
            {"stage": "Evidence and Outcome", "detail": "Witnesses, documents, and final arguments shape the outcome."},
        ]

        return {
            "court_flow": {
                "sections_considered": sections,
                "severity_basis": level,
                "legal_stages": stages,
                "timeline_estimate": timeline[level],
                "possible_outcomes": outcomes[level],
                "user_involvement": user_involvement,
            }
        }
