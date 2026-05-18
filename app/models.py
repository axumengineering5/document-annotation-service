"""
models.py — dynamic model loader
Reads MODEL env var to select which local checkpoint to load.

Supported values (set via --env MODEL=... in docker run):
  mistral   → document_models/mistralai--Mistral-7B-Instruct-v0.3
  qwen      → document_models/Qwen--Qwen2.5-VL-7B-Instruct
  nuextract → document_models/numind--NuExtract-2.0-8B  (default)
"""

import os
from pathlib import Path

MODEL_MAP = {
    "mistral":   "mistralai--Mistral-7B-Instruct-v0.3",
    "qwen":      "Qwen--Qwen2.5-VL-7B-Instruct",
    "nuextract": "numind--NuExtract-2.0-8B",
}

DEFAULT_MODEL = "nuextract"


def get_model_key() -> str:
    return os.environ.get("MODEL", DEFAULT_MODEL).lower()


def get_model_name() -> str:
    key = get_model_key()
    return MODEL_MAP.get(key, MODEL_MAP[DEFAULT_MODEL])


def get_model_path() -> Path:
    name = get_model_name()
    # Resolve relative to repo root regardless of cwd
    base = Path(__file__).parent.parent / "document_models" / name
    if not base.exists():
        raise FileNotFoundError(
            f"Model directory not found: {base}\n"
            f"Run: python scripts/download_models.py --model {get_model_key()}"
        )
    return base


def load_model():
    """
    Load and return (tokenizer, model) from the selected checkpoint.

    In this skeleton the weights are stubs, so we return None placeholders.
    Replace the body below with real HuggingFace loading once weights are present:

        from transformers import AutoTokenizer, AutoModelForCausalLM
        path = str(get_model_path())
        tokenizer = AutoTokenizer.from_pretrained(path)
        model = AutoModelForCausalLM.from_pretrained(path, device_map="auto")
        return tokenizer, model
    """
    path = get_model_path()
    print(f"[models] Loading model from {path}  (stub — no real weights)")
    return None, None  # tokenizer, model
