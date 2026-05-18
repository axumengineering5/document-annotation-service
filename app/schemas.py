"""
schemas.py — Pydantic models for job state and annotation output
"""

from typing import Optional, List
from pydantic import BaseModel


class AnnotationResult(BaseModel):
    summary: str
    document_type: str          # pdf | spreadsheet | unknown
    key_entities: List[str]
    language: str = "en"
    page_count: Optional[int] = None
    model_used: str = ""
    raw_text_preview: str = ""


class Job(BaseModel):
    job_id: str
    filename: str
    status: str                 # queued | processing | done | failed
    result: Optional[dict] = None
    error: Optional[str] = None
