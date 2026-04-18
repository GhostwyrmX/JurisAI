from typing import Dict, List


class AnalyzerAgent:
    def run(self, query: str) -> Dict:
        normalized_query = query.strip()
        lower_query = normalized_query.lower()
        violent_crime_words = [
            "murder",
            "kill",
            "killed",
            "rape",
            "kidnap",
            "acid",
            "assault",
            "stab",
            "shoot",
        ]
        evasion_words = [
            "how to be free",
            "avoid punishment",
            "escape punishment",
            "escape police",
            "get away",
            "hide evidence",
            "destroy evidence",
            "avoid arrest",
            "not get caught",
        ]

        scenario_markers = [
            "threat",
            "attack",
            "stole",
            "steal",
            "murder",
            "kill",
            "assault",
            "fraud",
            "kidnap",
            "rape",
            "molest",
            "knife",
            "gun",
            "complaint",
            "fir",
        ]
        question_markers = ["what", "which", "explain", "define", "punishment", "section"]

        query_type = "scenario"
        if any(marker in lower_query for marker in question_markers) and not any(
            marker in lower_query for marker in scenario_markers
        ):
            query_type = "question"

        extracted_flags = {
            "mentions_weapon": any(word in lower_query for word in ["knife", "gun", "weapon", "acid"]),
            "mentions_injury": any(word in lower_query for word in ["injury", "hurt", "bleeding", "death", "killed"]),
            "mentions_property": any(word in lower_query for word in ["money", "phone", "wallet", "property", "gold"]),
            "mentions_threat": any(word in lower_query for word in ["threat", "threaten", "intimidate", "blackmail"]),
            "mentions_group": any(word in lower_query for word in ["group", "gang", "together", "multiple"]),
        }

        intents: List[str] = []
        if "fir" in lower_query or "complaint" in lower_query:
            intents.append("fir_support")
        if query_type == "scenario":
            intents.append("incident_analysis")
        else:
            intents.append("ipc_lookup")
        if "evidence" in lower_query or "proof" in lower_query:
            intents.append("evidence_support")

        summary_parts = [f"Detected a {query_type} style IPC query."]
        summary_parts.extend(
            label.replace("mentions_", "").replace("_", " ")
            for label, present in extracted_flags.items()
            if present
        )

        unsafe_request = any(word in lower_query for word in violent_crime_words) and any(
            phrase in lower_query for phrase in evasion_words
        )

        return {
            "query_type": query_type,
            "normalized_query": normalized_query,
            "intents": intents,
            "facts": extracted_flags,
            "understanding": " ".join(summary_parts).strip(),
            "unsafe_request": unsafe_request,
        }
