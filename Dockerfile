FROM python:3.10-slim

WORKDIR /app

# System dependencies
COPY packages.txt .
RUN apt-get update && \
    apt-get install -y $(cat packages.txt) wget && \
    rm -rf /var/lib/apt/lists/*

# Download Noto Sans Bengali font for PDF generation
RUN mkdir -p pdf_gen/fonts && \
    wget -q -O pdf_gen/fonts/NotoSansBengali-Regular.ttf \
    "https://fonts.gstatic.com/s/notosansbengali/v33/Cn-SJsCGWQxOjaGwMQ6fIiMywrNJIky6nvd8BjzVMvJx2mcSPVFpVEqE-6KmsolLudA.ttf"

# Python dependencies — install torch CPU-only wheel first (avoids 700 MB CUDA download)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    torch==2.10.0 torchvision \
    --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# App code — cache-bust: 2026-05-23
COPY . .

# Pre-cache the sentence-transformers embedding model so first-run load is instant
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2')" || true

# Build FAISS index from knowledge base (index files are gitignored; must be built at deploy time)
RUN python rag/build_index.py || true

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableXsrfProtection=false", \
     "--server.enableCORS=false"]
