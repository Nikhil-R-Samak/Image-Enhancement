# Use a lightweight Python base image 
FROM python:3.10-slim 

# Set working directory inside the container 
WORKDIR /app

# Copy your code and requirements file into the container 
COPY . /app

# Install system dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \ git \ && rm -rf /var/lib/apt/lists/*

# Install PyTorch first (CPU version) 
RUN pip install --no-cache-dir torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 

# Install BasicSR directly from GitHub (prebuilt, avoids local build issues) 
RUN pip install --no-cache-dir git+https://github.com/Xinntao/BasicSR.git 

# Install remaining Python dependencies 
RUN pip install --no-cache-dir -r requirements.txt 

# Expose the default port for FastAPI / Uvicorn 
EXPOSE 8000 

# Command to start the FastAPI app 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
