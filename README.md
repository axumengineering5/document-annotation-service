# Document Annotation Service

Event-driven REST service that accepts PDF/spreadsheet uploads, returns a job ID immediately, and annotates documents in the background using a local HuggingFace LLM.

---

## Architecture

```
POST /upload  →  job_id (instant)
                   └─ background thread
                        ├─ parsers.py   (pdfplumber / openpyxl)
                        ├─ models.py    (load from document_models/)
                        └─ worker.py    (annotate → store result)

GET /jobs/:id →  { status, result }
```

Jobs are held in an in-memory dict (`storage.py`). Swap for Redis or SQLite for persistence.

---

## Models

| Flag | HuggingFace repo | Best for |
|------|-----------------|----------|
| `mistral` | `mistralai/Mistral-7B-Instruct-v0.3` | Clean text-native PDFs, fast path |
| `qwen` | `Qwen/Qwen2.5-VL-7B-Instruct` | Scanned PDFs, visual/table-heavy docs |
| `nuextract` *(default)* | `numind/NuExtract-2.0-8B` | Schema-driven JSON extraction |

Weights live in `document_models/<model-dir>/` and are **never committed** (see `.gitignore`).

---

## Quick Start

### 1. Download real weights (optional — stubs work for dev)

```bash
pip install huggingface_hub
export HF_TOKEN=hf_...          # only needed for Mistral
python scripts/download_models.py --model nuextract
```

### 2. Run locally

```bash
pip install -r requirements.txt
MODEL=nuextract uvicorn app.main:app --reload
```

### 3. Run with Docker

```bash
# Build
docker build -t doc-annotator .

# Run with a specific model (weights mounted from host)
docker run -p 8000:8000 \
  -e MODEL=nuextract \
  -v $(pwd)/document_models:/app/document_models:ro \
  doc-annotator

# Swap model at runtime — no rebuild needed
docker run -p 8000:8000 -e MODEL=mistral \
  -v $(pwd)/document_models:/app/document_models:ro \
  doc-annotator
```

### 4. Docker Compose profiles

```bash
docker compose up                       # nuextract (default)
docker compose --profile mistral up     # Mistral-7B
docker compose --profile qwen up        # Qwen2.5-VL
```

---

## API

### `POST /upload`

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@invoice.pdf"
```

```json
{ "job_id": "c3f1...", "status": "queued", "model": "numind--NuExtract-2.0-8B" }
```

### `GET /jobs/{job_id}`

```bash
curl http://localhost:8000/jobs/c3f1...
```

```json
{
  "job_id": "c3f1...",
  "status": "done",
  "result": {
    "summary": "Invoice from Acme Corp for $4,200...",
    "document_type": "pdf",
    "key_entities": ["Acme Corp", "John Smith"],
    "language": "en",
    "page_count": 2,
    "model_used": "numind--NuExtract-2.0-8B"
  }
}
```

---

## Design Decisions

- **Threading over task queue** — simplest path that respects the timeout constraint. Background thread starts immediately and writes to the store; the caller polls `/jobs/:id`.
- **MODEL env var** — single flag, no config file needed. Docker `-e MODEL=qwen` is enough to switch models without a rebuild.
- **In-memory store** — sufficient for a skeleton/demo. Replace `JobStore` with Redis for multi-worker/multi-pod deployments.
- **Stub inference** — the annotation pipeline is fully wired; only the `model.generate()` call is stubbed. Dropping in real weights + uncommenting `transformers` in `requirements.txt` is the only change needed.

---

## What I'd Improve With Another Day

- Replace threading with **Celery + Redis** (retries, priorities, visibility timeout)
- Add **idempotency key** on `/upload` (hash of file content) to deduplicate re-uploads
- **Structured logging** (structlog) + OpenTelemetry traces per job
- **Cost tracking** — log token counts per inference call, aggregate by model
- `/jobs/{id}/cancel` endpoint
- Streaming progress updates via Server-Sent Events
- GPU-aware Dockerfile (`FROM nvidia/cuda:...`)

---

## Production Checklist

| Concern | Solution |
|---------|----------|
| Failure handling | Celery retry with exponential backoff |
| Idempotency | SHA-256 file hash as job key |
| Observability | Prometheus metrics + Grafana dashboard |
| Persistence | Redis or Postgres job store |
| Cost | Token-level accounting logged per job |
| Scaling | Worker pool behind a queue; model server (vLLM) separate from API |
| Security | File type validation, size limits, signed upload URLs |
