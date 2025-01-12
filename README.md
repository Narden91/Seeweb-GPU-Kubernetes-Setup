# GPU-Accelerated Processing Framework

## Author
Emanuele Nardone

## Overview
A containerized application that performs GPU-accelerated processing tasks using PyTorch, designed to run in a Seeweb Serverless GPU Cluster with NVIDIA A6000 GPUs. The framework supports two primary processing modes:

1. **Matrix Multiplication Benchmark**: Compares CPU and GPU performance for various matrix sizes
2. **Image Processing Pipeline**: Performs image transformations using both CPU and GPU, including Gaussian blur and color adjustments

Results are stored in S3-compatible storage, and container images are managed through GitHub Container Registry (GHCR).

## Features

### Core Features
- Dual processing modes: Matrix multiplication and Image processing
- Automatic GPU detection with CPU fallback
- Detailed performance metrics and speedup calculations
- Rich CLI output with colored performance indicators
- S3-compatible storage integration
- Comprehensive logging system
- Configurable via CLI arguments or environment variables

### Matrix Processing Features
- Configurable matrix sizes for benchmarking
- PyTorch-based CPU vs GPU computations
- Memory-efficient large matrix handling

### Image Processing Features
- Batch image processing capabilities
- Gaussian blur and color adjustment transformations
- Support for common image formats (PNG, JPG, JPEG)
- Parallel processing optimization

### Infrastructure Features
- NVIDIA CUDA 11.8.0 runtime support
- Kubernetes integration with GPU resource management
- GitHub Actions CI/CD pipeline
- Exponential backoff retry mechanism for S3 operations

## Project Structure
```
gpu-processing-framework/
├── benchmark_operations/      # Matrix multiplication operations
│   └── benchmark_operations.py
├── image_processing/         # Image processing operations
│   └── image_processing_operations.py
├── cli_operations/          # Command-line interface handling
│   └── cli_operations.py
├── config/                  # Configuration management
│   └── s3_config_handler.py
├── s3_operations/          # S3 storage operations
│   ├── s3_client.py       # Low-level S3 client with retry logic
│   └── s3_operations.py   # High-level S3 operations
├── .env.test              # Environment variables template
├── .gitignore             # Git ignore rules
├── Dockerfile             # NVIDIA CUDA-based container configuration
├── main.py               # Application entry point
├── python_image.yml      # Kubernetes pod configuration
└── requirements.txt      # Python dependencies
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
# S3 Configuration
S3_ENDPOINT_URL=your-s3-endpoint
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET=your-bucket-name

# Processing Configuration
PROCESSING_MODE=matrix|image  # Optional, defaults to matrix
MATRIX_SIZES=1000,2000,3000  # Optional for matrix mode
RAW_IMAGES_FOLDER=RawImages  # Optional for image mode
PROCESSED_IMAGES_FOLDER=ProcessedImages  # Optional for image mode
RESULTS_FOLDER=benchmark_results  # Optional
```

## Kubernetes Deployment

### 1. GPU Runtime Configuration
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

### 3. Create ConfigMap
You can create the ConfigMap either using a YAML file or kubectl command:

Option 1: Using YAML file (recommended)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prj-configmap
data:
  MATRIX_SIZES: "4000,5000,10000"
  PROCESSING_MODE: "matrix"  # or "image"
  RAW_IMAGES_FOLDER: "RawImages"
  PROCESSED_IMAGES_FOLDER: "ProcessedImages"
  RESULTS_FOLDER: "benchmark_results"
```

Apply with:
```bash
kubectl apply -f prj-configmap.yml
```

Option 2: Using kubectl command
```bash
kubectl create configmap prj-configmap \
  --from-literal=MATRIX_SIZES="4000,5000,10000" \
  --from-literal=PROCESSING_MODE="matrix" \
  --from-literal=RAW_IMAGES_FOLDER="RawImages" \
  --from-literal=PROCESSED_IMAGES_FOLDER="ProcessedImages" \
  --from-literal=RESULTS_FOLDER="benchmark_results"
```

### 4. Deploy the Application
```bash
kubectl apply -f manifest.yml
```

## CI/CD Pipeline
The project uses GitHub Actions for automated builds and deployments:

- Triggers on version tags (v*.*.*)
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

### 2. Run Matrix Multiplication Benchmark
```bash
# With default matrix sizes
python main.py --mode matrix

# With custom matrix sizes
python main.py --mode matrix --matrix-sizes 1000,2000,3000
```

### 3. Run Image Processing
```bash
# With default folders
python main.py --mode image

# With custom folders
python main.py --mode image \
  --raw-images-folder custom/raw \
  --processed-images-folder custom/processed
```

## Monitoring and Troubleshooting

### Pod Status and Logs
```bash
# Check pod status
kubectl get pods
kubectl describe pod python-test

# View logs
kubectl logs -f python-test

# Check GPU status
kubectl exec -it python-test -- nvidia-smi
```

### Common Issues and Solutions

1. **GPU Not Detected**
   - Verify runtime class configuration
   - Check NVIDIA device plugin status
   ```bash
   kubectl get pods -n kube-system | grep nvidia-device-plugin
   ```

2. **S3 Connection Issues**
   - Verify endpoint and credentials
   - Check network connectivity
   - Review exponential backoff settings

3. **Performance Optimization**
   - Monitor GPU memory usage
   - Adjust batch sizes for image processing
   - Consider matrix size limitations

## Output Structure

### Matrix Multiplication Results
Results are stored in `benchmark_results/` with format:
```
matrix_multiplication_benchmark_YYYYMMDD_HHMMSS.txt
```

Contents include:
- Device information (GPU model, memory)
- Matrix sizes tested
- CPU and GPU execution times
- Speedup calculations

### Image Processing Results
Results are stored in `ProcessedImages/` with:
- Processed images: `original_filename`
- Performance report: `processing_results_YYYYMMDD_HHMMSS.txt`

## License
Unicas & Seeweb