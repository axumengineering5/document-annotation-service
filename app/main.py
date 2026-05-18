"""
main.py — FastAPI entrypoint
Endpoints:
  POST /upload        → returns job_id immediately, fires background task
  GET  /jobs/{job_id} → returns annotation result or status
"""

import uuid
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.storage import JobStore
from app.worker import run_annotation
from app.models import get_model_name

app = FastAPI(title="Document Annotation Service")
store = JobStore()


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    content = await file.read()

    store.create(job_id, filename=file.filename)

    # Fire-and-forget background thread (swap for Celery/RQ in prod)
    thread = threading.Thread(
        target=run_annotation,
        args=(job_id, file.filename, content, store),
        daemon=True,
    )
    thread.start()

    return JSONResponse({"job_id": job_id, "status": "queued", "model": get_model_name()})


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
