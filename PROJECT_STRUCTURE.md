# JURIS AI Project Structure

## Root

```text
JurisAI/
├── ai-service-python/
├── backend-node/
├── dataset/
├── frontend/
├── legal_modules/
├── vector_index/
├── README.md
├── PROJECT_STRUCTURE.md
├── SERVICE_SETUP.md
└── MODEL_MANAGEMENT.md
```

## Frontend

```text
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── AIResponseDetails.js
│   │   ├── ChatInterface.js
│   │   ├── FormattedAIText.js
│   │   ├── IPCBrowser.js
│   │   ├── IPCMetadataPanel.js
│   │   ├── Navbar.js
│   │   ├── QueryHistory.js
│   │   └── ...
│   ├── contexts/
│   ├── App.js
│   ├── App.css
│   ├── index.css
│   └── ipcUtils.js
├── package.json
└── tailwind.config.js
```

### Frontend Notes

- `ChatInterface.js` contains the AI Assistant page, TTS trigger, and browser speech-to-text input.
- `AIResponseDetails.js` is the shared renderer used by chat and history details.
- `FormattedAIText.js` formats model output into readable sections and lists.
- `IPCMetadataPanel.js` renders structured IPC metadata cards.
- `Navbar.js` now includes mobile navigation behavior.

## Backend

```text
backend-node/
├── server.js
├── tests/
├── package.json
└── package-lock.json
```

### Backend Notes

- Handles auth, query history, and proxying to the Python AI service.
- Stores richer query metadata including charges, matched IPC sections, and referenced sections.

## AI Service

```text
ai-service-python/
├── main.py
├── cache/
├── metrics/
├── models/
├── scripts/
│   ├── build_vector_index.py
│   ├── download_models.py
│   └── ingest_dataset.py
├── services/
│   ├── charge_prediction.py
│   ├── llm_service.py
│   ├── rag_service.py
│   ├── translation_service.py
│   └── tts_service.py
├── tests/
├── utils/
│   ├── config.py
│   ├── logging.py
│   └── validation.py
└── requirements.txt
```

### AI Service Notes

- `validation.py` validates the expanded IPC dataset schema.
- `rag_service.py` builds richer embeddings from more dataset fields.
- `charge_prediction.py` now uses calibrated confidence instead of raw similarity only.
- `main.py` exposes retrieval, prediction, TTS, and IPC lookup endpoints.

## Dataset

```text
dataset/
└── ipc/
    └── ipc.json
```

The IPC dataset now powers:

- retrieval context
- search terms
- metadata cards
- scenario prediction hints
- related section lookup

## Vector Index

```text
vector_index/
├── ipc.index
└── ipc.index.meta
```

Rebuild the vector index whenever dataset content or retrieval fields change.
