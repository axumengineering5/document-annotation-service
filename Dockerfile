FROM python:3.11-slim

WORKDIR /app

# System deps for pdfplumber (poppler) if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source — model weights are mounted at runtime, not baked in
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create empty model dirs so path checks pass even without weights
RUN mkdir -p \
    document_models/mistralai--Mistral-7B-Instruct-v0.3 \
    document_models/Qwen--Qwen2.5-VL-7B-Instruct \
    document_models/numind--NuExtract-2.0-8B

# MODEL env var selects which checkpoint to use (mistral | qwen | nuextract)
ENV MODEL=nuextract
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
