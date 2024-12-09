FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files maintaining directory structure
COPY . .

# # Create results directory (if not already in project)
# RUN mkdir -p /app/results

# # Set environment variables
# ENV RESULTS_DIR=/app/results

# Command to run the script
CMD ["python3", "main.py"]