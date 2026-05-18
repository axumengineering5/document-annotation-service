"""
worker.py — background annotation agent

Orchestrates:
  1. Parse document (PDF or spreadsheet)
  2. Run model inference (or stub)
  3. Persist result via JobStore
"""

import json
import traceback

from app.models import load_model, get_model_name
from app.parsers import parse_document
from app.schemas import AnnotationResult
from app.storage import JobStore


def run_annotation(job_id: str, filename: str, content: bytes, store: JobStore):
    store.update(job_id, {"status": "processing"})
    try:
        # 1. Parse
        extracted_text = parse_document(filename, content)

        # 2. Load model (stub returns None, None)
        tokenizer, model = load_model()

        # 3. Annotate — real call or stub
        result = _annotate(filename, extracted_text, tokenizer, model)

        store.update(job_id, {"status": "done", "result": result.model_dump()})

    except Exception as exc:
        store.update(job_id, {
            "status": "failed",
            "error": traceback.format_exc(),
        })


def _annotate(filename: str, text: str, tokenizer, model) -> AnnotationResult:
    """
    Build the structured annotation.

    When model/tokenizer are real objects replace the stub block with:

        prompt = _build_prompt(filename, text)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        out = model.generate(**inputs, max_new_tokens=512)
        raw = tokenizer.decode(out[0], skip_special_tokens=True)
        payload = json.loads(raw)          # model must return JSON
        return AnnotationResult(**payload)

    For Qwen (vision) pass document images instead of text.
    For NuExtract pass the JSON template as part of the prompt.
    """

    # ── STUB: simulated annotation ──────────────────────────────────
    model_used = get_model_name()

    stub = {
        "summary": f"[STUB] Document '{filename}' processed by {model_used}.",
        "document_type": _guess_type(filename),
        "key_entities": ["Entity A", "Entity B"],
        "language": "en",
        "page_count": None,
        "model_used": model_used,
        "raw_text_preview": text[:300] if text else "",
    }
    return AnnotationResult(**stub)


def _guess_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return {
        "pdf":  "pdf",
        "xlsx": "spreadsheet",
        "xls":  "spreadsheet",
        "csv":  "spreadsheet",
    }.get(ext, "unknown")


def _build_prompt(filename: str, text: str) -> str:
    return (
        "Extract structured metadata from the following document and return ONLY "
        "valid JSON matching this schema:\n"
        '{"summary": str, "document_type": str, "key_entities": [str], '
        '"language": str, "page_count": int|null}\n\n'
        f"Filename: {filename}\n\nContent:\n{text[:4000]}"
    )
