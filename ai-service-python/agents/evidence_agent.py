from typing import Dict, List


class EvidenceAgent:
    def run(self, query: str, analysis: Dict, ipc_mapping: Dict) -> Dict:
        lower_query = query.lower()
        checklist: List[str] = [
            "Write a dated incident summary in your own words while events are fresh.",
            "Keep names, phone numbers, and addresses of witnesses if available.",
        ]

        if any(word in lower_query for word in ["phone", "message", "whatsapp", "email", "online", "fraud"]):
            checklist.append("Preserve screenshots, chats, call logs, emails, transaction IDs, and device metadata.")
        if any(word in lower_query for word in ["injury", "attack", "assault", "knife", "gun", "hurt"]):
            checklist.append("Collect medical records, injury photographs, hospital slips, and weapon descriptions if any.")
        if any(word in lower_query for word in ["theft", "stole", "robbery", "money", "gold", "wallet", "phone"]):
            checklist.append("Keep bills, ownership proof, bank entries, CCTV references, and missing property details.")
        if any(word in lower_query for word in ["house", "trespass", "break in", "entry"]):
            checklist.append("Preserve entry-point photos, CCTV clips, neighbour accounts, and property damage images.")

        titles = [item.get("title") for item in ipc_mapping.get("ipc_sections", []) if item.get("title")]
        if titles:
            checklist.append(f"Keep records that directly support the factual elements of these mapped offences: {', '.join(titles[:3])}.")

        return {
            "evidence_checklist": checklist,
            "preservation_note": "Do not edit digital files; preserve originals and copies where possible.",
        }
