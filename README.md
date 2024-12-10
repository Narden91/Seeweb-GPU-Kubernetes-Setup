# Matrix Multiplication Benchmark

## Overview
A containerized application that performs matrix multiplication benchmarks comparing CPU and GPU performance. 
The project is designed to run in a Seeweb Serverless GPU Cluster.
The project also utilize GitHub Container Registry (GHCR) for image storage and S3-compatible storage for results.

## Project Structure
```
matrix-benchmark/
├── benchmark_operations/      # Matrix multiplication and benchmark logic
│   ├── __init__.py
│   └── benchmark_operations.py
├── cli_operations/           # Command-line interface operations
│   ├── __init__.py
│   └── cli_operations.py
├── config/                   # Configuration management
│   ├── __init__.py
│   └── config.py
├── s3_operations/           # S3 storage operations
│   ├── __init__.py
│   └── s3_operations.py
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker container configuration
├── main.py                 # Main application entry point
├── matrix_config.yml       # ConfigMap for matrix sizes
├── python_image.yml        # Kubernetes pod configuration
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

## Kubernetes Setup

### 1. Create GitHub Container Registry Secret
```bash
# Create a Personal Access Token (PAT) in GitHub with read:packages scope
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT \
  --docker-email=YOUR_GITHUB_EMAIL
```

### 2. Create AWS Credentials Secret
```bash
# Create secret for S3 credentials
kubectl create secret generic s3-secrets \
  --from-literal=S3_ENDPOINT_URL='your-s3-endpoint' \
  --from-literal=AWS_ACCESS_KEY_ID='your-access-key' \
  --from-literal=AWS_SECRET_ACCESS_KEY='your-secret-key' \
  --from-literal=S3_BUCKET='your-bucket-name'
```

### 3. Apply ConfigMap for Matrix Sizes
```bash
# Apply the ConfigMap for matrix sizes
kubectl apply -f matrix_config.yml
```

### 4. Deploy the Application
```bash
# Deploy the pod
kubectl apply -f python_image.yml
```

## Configuration Files

### matrix_config.yml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: matrix-benchmark-config
data:
  MATRIX_SIZES: "1000,2000,3000,4000,5000"
```

### python_image.yml
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: python-test
  namespace: default
spec:
  restartPolicy: OnFailure
  runtimeClassName: seeweb-nvidia-1xa6000  # Adjust based on your cluster's GPU setup
  imagePullSecrets:
    - name: ghcr-secret
  containers:
  - name: nvidia
    image: "ghcr.io/your-username/k8s_test:latest"    
    imagePullPolicy: Always
    resources:
      limits:
        nvidia.com/gpu: "1"
    envFrom:
      - secretRef:
          name: s3-secrets
      - configMapRef:
          name: matrix-benchmark-config
```

## Kubernetes Operations

### Monitor Pod Status
```bash
# Check pod status
kubectl get pods

# View pod logs
kubectl logs -f python-test

# Describe pod for detailed information
kubectl describe pod python-test
```

### Delete Resources
```bash
# Delete pod
kubectl delete pod python-test

# Delete secrets
kubectl delete secret s3-secrets
kubectl delete secret ghcr-secret

# Delete ConfigMap
kubectl delete configmap matrix-benchmark-config
```

### Scale Resources (Optional)
```bash
# Create a deployment instead of a pod for scaling
kubectl create deployment matrix-benchmark --image=ghcr.io/your-username/k8s_test:latest

# Scale the deployment
kubectl scale deployment matrix-benchmark --replicas=3
```

## Development

### Local Testing
1. Build the Docker image:
   ```bash
   docker build -t ghcr.io/your-username/k8s_test:latest .
   ```

2. Push to GitHub Container Registry:
   ```bash
   docker login ghcr.io -u YOUR_GITHUB_USERNAME -p YOUR_GITHUB_PAT
   docker push ghcr.io/your-username/k8s_test:latest
   ```

## Results
- Benchmark results are automatically saved to the configured S3 bucket
- Results location: `s3://your-bucket-name/benchmark_results/`
- Each file includes device information, matrix sizes, and timing comparisons

## Requirements
- Kubernetes cluster with GPU support
- NVIDIA Container Toolkit
- Access to GitHub Container Registry
- S3-compatible storage
- kubectl CLI tool

## CI/CD with GitHub Actions

### GitHub Actions Setup

1. **Create GitHub Secrets**
   Navigate to your repository's Settings > Secrets and Variables > Actions and add:
   ```
   GHCR_TOKEN          # GitHub PAT with write:packages permission
   GHCR_USERNAME       # Your GitHub username
   ```

2. **Workflow Configuration**
   Create `.github/workflows/docker-build.yml`:
   ```yaml
   name: Docker Build and Push

   on:
     push:
       tags:
         - 'v*'  # Triggers on version tags (v1.0.0, v2.1.0, etc.)

   env:
     REGISTRY: ghcr.io
     IMAGE_NAME: ${{ github.repository }}

   jobs:
     build-and-push:
       runs-on: ubuntu-latest
       permissions:
         contents: read
         packages: write

       steps:
         - name: Checkout repository
           uses: actions/checkout@v4

         - name: Log in to the Container registry
           uses: docker/login-action@v3
           with:
             registry: ${{ env.REGISTRY }}
             username: ${{ github.actor }}
             password: ${{ secrets.GITHUB_TOKEN }}

         - name: Extract metadata for Docker
           id: meta
           uses: docker/metadata-action@v5
           with:
             images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
             tags: |
               type=semver,pattern={{version}}
               type=sha

         - name: Build and push Docker image
           uses: docker/build-push-action@v5
           with:
             context: .
             push: true
             tags: ${{ steps.meta.outputs.tags }}
             labels: ${{ steps.meta.outputs.labels }}
   ```

3. **Trigger Image Build**
   ```bash
   # Create and push a new version tag
   git tag v1.0.0
   git push origin v1.0.0
   ```

### Manual Image Build and Push
```bash
# Build locally
docker build -t ghcr.io/your-username/k8s_test:latest .

# Login to GHCR
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin

# Push image
docker push ghcr.io/your-username/k8s_test:latest
```

### Image Versioning
- Images are tagged with:
  - Semantic version (from git tag): `v1.0.0`
  - Git SHA: `sha-f2d3aa2`
- Latest version is always available as `:latest`

### Access Control
1. Make your GitHub repository public or configure package access
2. Navigate to package settings in GitHub
3. Add collaborators or teams for private packages

## Quick Start Guide

1. **Set Up Repository**
   ```bash
   # Clone repository
   git clone https://github.com/your-username/k8s_test.git
   cd k8s_test
   ```

2. **Configure GitHub Actions**
   - Add required secrets to repository
   - Push code to trigger workflow

3. **Deploy to Kubernetes**
   ```bash
   # Create required secrets and configmaps
   kubectl create secret docker-registry ghcr-secret ...
   kubectl create secret generic s3-secrets ...
   kubectl apply -f matrix_config.yml

   # Deploy application
   kubectl apply -f python_image.yml
   ```

4. **Monitor Deployment**
   ```bash
   # Watch pod status
   kubectl get pods -w
   ```

## Troubleshooting

### Common Issues
1. Pod stuck in "Pending" state:
   ```bash
   kubectl describe pod python-test
   ```
   - Check for GPU availability
   - Verify node selector/runtime class

2. Image pull errors:
   ```bash
   kubectl describe pod python-test | grep -A 10 Events
   ```
   - Verify ghcr-secret is correctly configured
   - Check image name and tag

3. S3 connection issues:
   ```bash
   kubectl logs python-test
   ```
   - Verify s3-secrets values
   - Check S3 endpoint accessibility

## License

Unicas & Seeweb