# Use python3.11 
FROM python:3.11-slim

# Avoid interactive prompts and speed up build
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# System dependencies for OpenCV and scientific libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-opencv \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

# Copy your full project (adjust if needed)
COPY . .

# Default working directory for scripts
WORKDIR /app

# Default command — can be changed when running
CMD ["python", "run_pipeline.py"]