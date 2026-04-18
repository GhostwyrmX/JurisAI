# Model Management

JURIS AI currently uses Ollama for local model inference.

## Primary Model

- `qwen2.5-coder:7b`

## Model Usage

- legal question answering
- IPC-grounded response generation
- scenario analysis support

Embeddings are handled separately through Sentence Transformers in the Python AI service.

## Install the Model

```bash
ollama pull qwen2.5-coder:7b
```

## Start Ollama

```bash
ollama serve
```

## Check Installed Models

```bash
ollama list
```

## Model Requirements File

The project also keeps model requirements in:

```text
ai-service-python/models/requirements.txt
```

Use the helper script if needed:

```bash
cd ai-service-python
python scripts/download_models.py
```

## Operational Notes

- Keep the Ollama model available before starting the Python AI service.
- If you change models, restart the Python AI service after Ollama is ready.
- For dataset or retrieval updates, rebuilding the FAISS index is still required.

## Troubleshooting

### Model not found

```bash
ollama list
ollama pull qwen2.5-coder:7b
```

### Ollama is running but AI service still fails

- verify `OLLAMA_URL` in `ai-service-python/.env`
- restart the Python AI service
- confirm the model name matches the configured one
