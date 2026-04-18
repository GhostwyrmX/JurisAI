from typing import Dict, List


class IPCPromptEngine:
    @staticmethod
    def build_structured_prompt(query: str, context_sections: List[Dict]) -> str:
        context_lines = []
        for item in context_sections[:5]:
            context_lines.append(
                f"Section {item.get('section')}: {item.get('title')} - {item.get('description')}"
            )

        context_block = "\n".join(context_lines) if context_lines else "No matched IPC sections."
        return (
            "You are JurisAI Pro.\n"
            "Stay strictly within the Indian Penal Code.\n"
            "Do not mention any other law.\n"
            "Return guidance grounded only in the supplied IPC context.\n\n"
            f"Query: {query}\n"
            f"IPC Context:\n{context_block}\n"
        )
