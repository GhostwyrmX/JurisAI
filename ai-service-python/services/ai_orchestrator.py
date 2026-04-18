import asyncio
import hashlib
import json
from typing import Dict, List

from agents import (
    ActionAgent,
    AnalyzerAgent,
    AudioAgent,
    CourtFlowAgent,
    EvidenceAgent,
    FIRAgent,
    IPCMapperAgent,
    PersonaAgent,
    SeverityAgent,
    ValidatorAgent,
)
from cache.redis_cache import cache
from prompts.ipc_prompt_engine import IPCPromptEngine
from utils.logging import log_error


class AIOrchestrator:
    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.ipc_mapper = IPCMapperAgent()
        self.severity = SeverityAgent()
        self.evidence = EvidenceAgent()
        self.action = ActionAgent()
        self.fir = FIRAgent()
        self.court_flow = CourtFlowAgent()
        self.validator = ValidatorAgent()
        self.persona = PersonaAgent()
        self.audio = AudioAgent()

    def _cache_key(self, query: str, persona: str, language: str) -> str:
        digest = hashlib.sha256(f"{query}|{persona}|{language}".encode("utf-8")).hexdigest()
        return f"jurisai_pro:{digest}"

    async def _run_parallel(self, query: str, analysis: Dict):
        ipc_task = asyncio.to_thread(self.ipc_mapper.run, query, analysis)
        ipc_mapping = await ipc_task

        severity_task = asyncio.to_thread(self.severity.run, query, ipc_mapping, analysis)
        evidence_task = asyncio.to_thread(self.evidence.run, query, analysis, ipc_mapping)
        severity, evidence = await asyncio.gather(severity_task, evidence_task)
        return ipc_mapping, severity, evidence

    async def process(self, query: str, persona: str = "general", language: str = "english") -> Dict:
        cache_key = self._cache_key(query, persona, language)
        cached = cache.get(cache_key)
        if cached:
            cached["cache_hit"] = True
            return cached

        analysis = await asyncio.to_thread(self.analyzer.run, query)
        if analysis.get("unsafe_request"):
            refusal_payload = self._build_refusal_payload(persona, language)
            try:
                cache.set(cache_key, refusal_payload, ttl=300)
            except Exception as exc:
                log_error(f"Failed to cache refusal payload: {exc}")
            return refusal_payload

        ipc_mapping, severity, evidence = await self._run_parallel(query, analysis)
        action_plan = await asyncio.to_thread(self.action.run, analysis, severity, ipc_mapping, evidence)
        fir = await asyncio.to_thread(self.fir.run, query, analysis, ipc_mapping)
        court_flow = await asyncio.to_thread(self.court_flow.run, severity, ipc_mapping)

        payload = {
            "understanding": analysis.get("understanding"),
            "severity": severity,
            "ipc_sections": ipc_mapping.get("ipc_sections", []),
            "steps": action_plan.get("steps", []),
            "complaint_draft": fir.get("complaint_draft"),
            "evidence_checklist": evidence.get("evidence_checklist", []),
            "court_flow": court_flow.get("court_flow", {}),
            "tips": action_plan.get("tips", []),
            "donts": action_plan.get("donts", []),
            "audio_text": "",
            "matched_sections": ipc_mapping.get("matched_sections", []),
            "charges": ipc_mapping.get("charges", []),
            "language": language,
            "prompt_used": IPCPromptEngine.build_structured_prompt(query, ipc_mapping.get("ipc_sections", [])),
        }

        validated = await asyncio.to_thread(self.validator.run, payload, ipc_mapping)
        with_persona = await asyncio.to_thread(self.persona.run, validated, persona)
        final_payload = await asyncio.to_thread(self.audio.run, with_persona)
        final_payload["cache_hit"] = False

        try:
            cache.set(cache_key, final_payload, ttl=3600)
        except Exception as exc:
            log_error(f"Failed to cache JurisAI Pro payload: {exc}")

        return final_payload

    def _build_refusal_payload(self, persona: str, language: str) -> Dict:
        text = (
            "I can't help with avoiding arrest, punishment, or investigation for violent crime. "
            "If this relates to a real incident, the safest next step is to contact a lawyer immediately "
            "and surrender or cooperate with the authorities."
        )
        return {
            "understanding": text,
            "severity": {
                "label": "HIGH",
                "level": "HIGH",
                "rationale": ["Request seeks help to evade accountability for a violent offence."],
                "urgency_note": "Seek urgent legal counsel and follow lawful process.",
            },
            "ipc_sections": [],
            "steps": [
                {
                    "title": "Get legal representation",
                    "detail": "Contact a licensed criminal lawyer immediately.",
                },
                {
                    "title": "Follow lawful process",
                    "detail": "Do not destroy evidence or evade authorities; cooperate through counsel.",
                },
            ],
            "complaint_draft": None,
            "evidence_checklist": [],
            "court_flow": {},
            "tips": [],
            "donts": [
                "Do not seek help to hide evidence, evade police, or avoid punishment.",
            ],
            "audio_text": text,
            "matched_sections": [],
            "charges": [],
            "language": language,
            "prompt_used": None,
            "persona": persona,
            "persona_note": "Safety refusal applied.",
            "analysis": text,
            "complete_response": text,
            "sections_referenced": [],
            "validation": {
                "ipc_only": True,
                "validated_sections": [],
                "errors": ["unsafe_request_blocked"],
            },
            "cache_hit": False,
            "refusal": True,
        }

    async def stream(self, query: str, persona: str = "general", language: str = "english"):
        payload = await self.process(query, persona=persona, language=language)
        chunks: List[Dict] = [
            {"type": "status", "message": "Analyzing IPC context"},
            {"type": "understanding", "data": payload.get("understanding")},
            {"type": "severity", "data": payload.get("severity")},
            {"type": "ipc_sections", "data": payload.get("ipc_sections")},
            {"type": "steps", "data": payload.get("steps")},
            {"type": "evidence", "data": payload.get("evidence_checklist")},
            {"type": "court_flow", "data": payload.get("court_flow")},
            {"type": "final", "data": payload},
        ]

        for chunk in chunks:
            yield json.dumps(chunk) + "\n"
            await asyncio.sleep(0.05)


ai_orchestrator = AIOrchestrator()
