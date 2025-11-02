# Use python3.11 
FROM python:3.11-slim

WORKDIR /workspace
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

RUN python3.11 -m pip install --upgrade pip setuptools wheel

# Copy and install Python requirements
COPY requirements.txt .
RUN python3.11 -m pip install -r requirements.txt
