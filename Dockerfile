# Use NVIDIA CUDA base image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY matrix_helper.py .
COPY main.py .

# Create directory for results
RUN mkdir /app/results

# Set environment variable for results directory
ENV RESULTS_DIR=/app/results

# Command to run the script
CMD ["python3", "main.py"]