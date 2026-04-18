from typing import Dict


class AudioAgent:
    def run(self, payload: Dict) -> Dict:
        severity_label = payload.get("severity", {}).get("label", "LOW")
        section_summary = ", ".join(
            f"Section {item.get('section')}" for item in payload.get("ipc_sections", [])[:3]
        )
        steps = payload.get("steps", [])[:2]
        step_summary = " ".join(step.get("title", "") for step in steps)

        payload["audio_text"] = (
            f"{payload.get('understanding', '')} "
            f"Severity is {severity_label}. "
            f"Relevant IPC references include {section_summary or 'no confirmed section yet'}. "
            f"Next steps: {step_summary}."
        ).strip()
        return payload
