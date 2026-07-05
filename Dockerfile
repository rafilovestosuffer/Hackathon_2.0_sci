FROM python:3.10-slim

WORKDIR /app

# System dependencies — packages.txt + nginx + supervisor for dual-service routing
COPY packages.txt .
RUN apt-get update && \
    apt-get install -y $(cat packages.txt) wget nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

# Download Noto Sans Bengali font for PDF generation
RUN mkdir -p pdf_gen/fonts && \
    wget -q -O pdf_gen/fonts/NotoSansBengali-Regular.ttf \
    "https://fonts.gstatic.com/s/notosansbengali/v33/Cn-SJsCGWQxOjaGwMQ6fIiMywrNJIky6nvd8BjzVMvJx2mcSPVFpVEqE-6KmsolLudA.ttf"

# Python dependencies — install torch CPU-only wheel first (avoids 700 MB CUDA download)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    torch==2.10.0 torchvision \
    --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# App code — cache-bust: 2026-05-23
COPY . .

# Pre-cache the sentence-transformers embedding model so first-run load is instant
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')" || true

# Build FAISS index from knowledge base (index files are gitignored; must be built at deploy time)
RUN python rag/build_index.py || true

# nginx needs to write to these dirs as non-root if HF runs us as non-root
RUN mkdir -p /tmp/nginx_client_body /var/lib/nginx /var/log/nginx && \
    chmod -R 777 /tmp /var/lib/nginx /var/log/nginx

# HF Spaces requires port 7860 — nginx terminates here, routes to
# uvicorn (webhook) on :8000 and streamlit (UI) on :8501 internally.
EXPOSE 7860

CMD ["supervisord", "-c", "/app/deploy/supervisord.conf"]
