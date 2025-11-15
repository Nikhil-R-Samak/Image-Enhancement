# Use a lightweight Python base image 
FROM python:3.10-slim

# Set working directory 
WORKDIR /app

# Copy project files 
COPY . /app

# Install system dependencies required by OpenCV + Real-ESRGAN
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU
RUN pip install --no-cache-dir torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1

# Install BasicSR
RUN pip install --no-cache-dir git+https://github.com/Xinntao/BasicSR.git

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Cloud Run port
EXPOSE 8080

# Start FastAPI
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]

