# JurisAI Pro Agents

## Flow

User Query
-> `AnalyzerAgent`
-> parallel `IPCMapperAgent`, `SeverityAgent`, `EvidenceAgent`
-> `ActionAgent`
-> `FIRAgent`
-> `CourtFlowAgent`
-> `ValidatorAgent`
-> `PersonaAgent`
-> `AudioAgent`

## Agents

- `AnalyzerAgent`: Detects whether the request is an IPC question or incident scenario and extracts basic factual flags.
- `IPCMapperAgent`: Maps the query to IPC sections using the existing RAG and charge prediction services.
- `SeverityAgent`: Assigns `HIGH`, `MEDIUM`, or `LOW` urgency using query facts and mapped section signals.
- `EvidenceAgent`: Builds a practical evidence checklist based on the incident pattern.
- `ActionAgent`: Produces step-by-step next actions, tips, and don'ts.
- `FIRAgent`: Drafts a ready-to-edit police complaint / FIR-style submission.
- `CourtFlowAgent`: Predicts likely complaint, investigation, filing, and court stages.
- `ValidatorAgent`: Ensures output stays IPC-only and filters unvalidated section references.
- `PersonaAgent`: Adapts tone for `lawyer`, `police`, `student`, `general`, or `journalist` without changing logic.
- `AudioAgent`: Produces concise narration text for browser speech playback.

## Backward Compatibility

- Existing FastAPI endpoints `/rag`, `/predict-charges`, and `/generate-audio` remain available.
- Existing Node endpoint `/chat` still returns the original fields while now including `structured_response`.
- New streaming endpoint: `/chat/stream` via Node and `/pro/stream` via FastAPI.
