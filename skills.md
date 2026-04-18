# JurisAI Pro Skills

## IPC Mapping

- Reuse FAISS + sentence-transformer retrieval for direct IPC lookup.
- Reuse charge prediction scoring for incident-style inputs.
- Limit all mapped sections to validated IPC dataset entries only.

## Severity Detection

- `HIGH`: death, rape, kidnapping, grievous harm, weapon-heavy incidents.
- `MEDIUM`: assault, robbery, threat, extortion, fraud, clear bodily or coercive harm.
- `LOW`: informational or lower-immediacy IPC guidance.

## FIR Drafting

- Convert the user narrative into a factual complaint structure.
- Keep the draft editable and clearly marked as a complaint template.
- Mention IPC sections as possible references only.

## Court Prediction

- Use stage templates instead of expensive full-generation reasoning.
- Return legal stages, likely timeline, possible outcomes, and user involvement.
- Keep predictions informative and non-final.

## Persona Adaptation

- Supported personas: `lawyer`, `police`, `student`, `general`, `journalist`.
- Persona changes tone and presentation only.
- Legal logic, severity, and mapped IPC sections stay unchanged.
