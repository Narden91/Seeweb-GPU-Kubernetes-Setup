# Python Project Template with k8s Serverless Architecture

# Author

Emanuele Nardone

## Overview
A containerized application that performs matrix multiplication benchmarks comparing CPU and GPU performance using PyTorch. The project is designed to run in a Seeweb Serverless GPU Cluster with NVIDIA A6000 GPUs. Results are stored in S3-compatible storage, and container images are managed through GitHub Container Registry (GHCR).

## Features
- CPU vs GPU matrix multiplication benchmarking
- Configurable matrix sizes via CLI arguments or environment variables
- Automatic GPU detection and fallback to CPU
- Detailed performance metrics and speedup calculations
- S3-compatible storage for benchmark results
- Rich CLI output with colored performance indicators
- Exponential backoff retry mechanism for S3 operations
- Comprehensive logging system

## Project Structure
```
matrix-benchmark/
├── benchmark_operations/      # Matrix multiplication and benchmark logic
│   └── benchmark_operations.py  # PyTorch-based CPU/GPU computations
├── cli_operations/           # Command-line interface operations
│   └── cli_operations.py     # CLI argument parsing and result display
├── config/                   # Configuration management
│   └── s3_config_handler.py  # S3 credentials and configuration
├── s3_operations/           # S3 storage operations
│   ├── s3_client.py         # Low-level S3 client with retry logic
│   └── s3_operations.py     # High-level S3 operations
├── .env.test               # Template for environment variables
├── .gitignore              # Git ignore rules
├── Dockerfile              # NVIDIA CUDA-based container configuration
├── main.py                 # Application entry point
├── python_image.yml        # Kubernetes pod configuration
└── requirements.txt        # Python dependencies
```

## Prerequisites
- Kubernetes cluster with NVIDIA GPU support
- NVIDIA Container Toolkit
- Access to GitHub Container Registry
- S3-compatible storage
- kubectl CLI tool
- Python 3.8+ (for local development)

## Environment Variables
Create a `.env` file based on `.env.test`:
```bash
S3_ENDPOINT_URL=your-s3-endpoint
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET=your-bucket-name
MATRIX_SIZES=1000,2000,3000  # Optional, can be set via CLI
```

## Kubernetes Deployment

### 1. GPU Runtime Configuration
The project uses the `seeweb-nvidia-1xa6000` runtime class for NVIDIA A6000 GPU access:
```yaml
spec:
  runtimeClassName: seeweb-nvidia-1xa6000
  containers:
    - resources:
        limits:
          nvidia.com/gpu: "1"
```

### 2. Create Required Secrets
```bash
# GitHub Container Registry credentials
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT \
  --docker-email=YOUR_GITHUB_EMAIL

# S3 credentials
kubectl create secret generic s3-secrets \
  --from-literal=S3_ENDPOINT_URL='your-s3-endpoint' \
  --from-literal=AWS_ACCESS_KEY_ID='your-access-key' \
  --from-literal=AWS_SECRET_ACCESS_KEY='your-secret-key' \
  --from-literal=S3_BUCKET='your-bucket-name'
```

### 3. Create ConfigMap for Matrix Sizes
```bash
kubectl create configmap matrix-benchmark-config \
  --from-literal=MATRIX_SIZES="1000,2000,3000,4000,5000"
```

### 4. Deploy the Application
```bash
kubectl apply -f python_image.yml
```

## CI/CD Pipeline
The project uses GitHub Actions for automated builds and deployments:

- Builds trigger on version tags (v*.*.*)
- Uses NVIDIA CUDA 11.8.0 base image
- Pushes to GitHub Container Registry
- Tags images with semantic version and Git SHA

### Triggering a Build
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Local Development

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Build Docker Image
```bash
docker build -t ghcr.io/your-username/matrix-benchmark:dev .
```

### 3. Run Locally
```bash
# With default matrix sizes
python main.py

# With custom matrix sizes
python main.py --matrix-sizes 1000,2000,3000
```

## Monitoring and Troubleshooting

### Pod Status
```bash
# Check pod status
kubectl get pods
kubectl describe pod python-test

# View logs
kubectl logs -f python-test
```

### Common Issues and Solutions

1. **GPU Not Detected**
   - Check runtime class configuration
   - Verify NVIDIA device plugin is running
   ```bash
   kubectl get pods -n kube-system | grep nvidia-device-plugin
   ```

2. **S3 Connection Issues**
   - The application implements exponential backoff
   - Check S3 endpoint and credentials
   - Review pod logs for specific error messages

3. **Performance Issues**
   - Monitor GPU utilization:
   ```bash
   kubectl exec -it python-test -- nvidia-smi
   ```
   - Check memory allocation in logs

## Benchmark Results
Results are stored in the S3 bucket under `benchmark_results/` with the format:
```
matrix_multiplication_benchmark_YYYYMMDD_HHMMSS.txt
```

Each result file contains:
- Device information (GPU model, memory)
- Matrix sizes tested
- CPU and GPU execution times
- Speedup calculations

## License
Unicas & Seeweb