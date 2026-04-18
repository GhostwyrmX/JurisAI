from typing import Dict


class PersonaAgent:
    PERSONA_OPENERS = {
        "lawyer": "Professional IPC briefing:",
        "police": "Operational IPC note:",
        "student": "Study-oriented IPC explanation:",
        "general": "Plain-language IPC guidance:",
        "journalist": "Public-facing IPC summary:",
    }

    PERSONA_TONES = {
        "lawyer": "Use concise professional drafting with issue-focused phrasing.",
        "police": "Use operational, report-friendly phrasing focused on immediate steps.",
        "student": "Use explanatory language that highlights legal elements and structure.",
        "general": "Use simple, direct language without legal jargon where possible.",
        "journalist": "Use neutral, public-interest language suited for accurate reporting.",
    }

    def run(self, payload: Dict, persona: str) -> Dict:
        normalized_persona = persona if persona in self.PERSONA_OPENERS else "general"
        opener = self.PERSONA_OPENERS[normalized_persona]
        tone_note = self.PERSONA_TONES[normalized_persona]

        payload["persona"] = normalized_persona
        payload["persona_note"] = tone_note
        payload["understanding"] = f"{opener} {payload.get('understanding', '')}".strip()
        payload["analysis"] = self._build_analysis_text(payload)
        payload["complete_response"] = payload["analysis"]
        return payload

    def _build_analysis_text(self, payload: Dict) -> str:
        lines = [
            f"**Understanding**\n{payload.get('understanding', '')}",
            f"**Severity**\n{payload.get('severity', {}).get('label', 'LOW')}: {' '.join(payload.get('severity', {}).get('rationale', []))}",
        ]

        sections = payload.get("ipc_sections", [])
        if sections:
            section_lines = [
                f"- Section {item.get('section')}: {item.get('title')} (confidence {int(float(item.get('score', 0)) * 100)}%)"
                for item in sections
            ]
            lines.append("**IPC Sections**\n" + "\n".join(section_lines))

        steps = payload.get("steps", [])
        if steps:
            step_lines = [f"- {step.get('title')}: {step.get('detail')}" for step in steps]
            lines.append("**Action Steps**\n" + "\n".join(step_lines))

        evidence = payload.get("evidence_checklist", [])
        if evidence:
            lines.append("**Evidence Checklist**\n" + "\n".join(f"- {item}" for item in evidence))

        court_flow = payload.get("court_flow", {})
        if court_flow:
            lines.append(
                "**Court Flow**\n"
                f"- Timeline: {court_flow.get('timeline_estimate', '')}\n"
                + "\n".join(f"- Possible outcome: {item}" for item in court_flow.get("possible_outcomes", [])[:3])
            )

        return "\n\n".join(lines)
