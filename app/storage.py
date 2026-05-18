"""
storage.py — simple in-memory job store

Swap the dict for Redis (redis-py) or SQLite (sqlite3) for persistence.
Redis example:
    r = redis.Redis(host="redis", port=6379)
    r.set(job_id, json.dumps(data), ex=86400)
"""

import threading
from typing import Optional


class JobStore:
    def __init__(self):
        self._jobs: dict = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, filename: str):
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "filename": filename,
                "status": "queued",
                "result": None,
                "error": None,
            }

    def update(self, job_id: str, fields: dict):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(fields)

    def get(self, job_id: str) -> Optional[dict]:
        with self._lock:
            return self._jobs.get(job_id)
