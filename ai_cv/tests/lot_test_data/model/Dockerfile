# Use AMD ROCm PyTorch base
FROM rocm/pytorch:rocm6.4.2_ubuntu22.04_py3.11_pytorch_release_2.5.1

# Set working directory inside container
WORKDIR /workspace


RUN apt-get update && apt-get install -y \
    git \
    python3.11-venv \
    python3.11-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3.11 -m pip install --upgrade pip setuptools wheel

# Copy and install Python requirements
COPY requirements.txt .
RUN python3.11 -m pip install -r requirements.txt

# Install Ultralytics from GitHub
RUN python3.11 -m pip install git+https://github.com/ultralytics/ultralytics.git@main

# Copy your script into the container (optional; host mount works too)
# COPY train_model.py ./train_model.py

# Default command (can be overridden in docker-compose)
CMD ["python3", "/workspace/model/train_model.py"]
