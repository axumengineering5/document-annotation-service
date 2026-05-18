#!/usr/bin/env python3
"""
download_models.py — pull real weights from HuggingFace Hub

Usage:
  python scripts/download_models.py --model nuextract   # default
  python scripts/download_models.py --model mistral
  python scripts/download_models.py --model qwen
  python scripts/download_models.py --all               # download all three

Requires:
  pip install huggingface_hub
  HF_TOKEN env var for gated models (e.g. Mistral)
"""

import argparse
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEST_ROOT = REPO_ROOT / "document_models"

MODEL_MAP = {
    "mistral":   ("mistralai/Mistral-7B-Instruct-v0.3",  "mistralai--Mistral-7B-Instruct-v0.3"),
    "qwen":      ("Qwen/Qwen2.5-VL-7B-Instruct",         "Qwen--Qwen2.5-VL-7B-Instruct"),
    "nuextract": ("numind/NuExtract-2.0-8B",              "numind--NuExtract-2.0-8B"),
}


def download(key: str):
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        raise SystemExit("Install huggingface_hub:  pip install huggingface_hub")

    repo_id, local_dir_name = MODEL_MAP[key]
    dest = DEST_ROOT / local_dir_name
    dest.mkdir(parents=True, exist_ok=True)

    token = os.environ.get("HF_TOKEN")
    print(f"Downloading {repo_id} → {dest}")
    snapshot_download(
        repo_id=repo_id,
        local_dir=str(dest),
        token=token,
        ignore_patterns=["*.msgpack", "flax_model*", "tf_model*", "rust_model*"],
    )
    print(f"Done: {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=list(MODEL_MAP.keys()), default="nuextract")
    parser.add_argument("--all", action="store_true", help="Download all models")
    args = parser.parse_args()

    targets = list(MODEL_MAP.keys()) if args.all else [args.model]
    for key in targets:
        download(key)
