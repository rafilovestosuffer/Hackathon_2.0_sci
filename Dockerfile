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

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
