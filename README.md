# k8s_test

## Overview
This project performs matrix multiplication benchmarks using both CPU and GPU, and saves the results to an S3 bucket. It is designed to run in a Kubernetes environment with GPU support.

## Project Structure
```
k8s_test/
├── .github
│   └── workflows
│       └── docker_build.yml   # Recipe to save the docker image on GITHUB using version tagging
├── config                
│   ├── __init__.py
│   └── config.py              # Configuration file for S3 endpoint and credentials
├── main.py                    # Main script
├── matrix_helper.py           # Helper functions
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image configuration
└── python_image.yml           # Kubernetes pod configuration
```

## Usage

1. Deploy the Kubernetes pod:
   ```sh
   kubectl apply -f python_image.yml
   ```

2. Check the logs to see the benchmark results:
   ```sh
   kubectl logs python-pod
   ```

## Running the Benchmark
The main script to run the benchmark is `main.py`. It initializes the `MatrixOperations` class, runs the benchmark for different matrix sizes, and saves the results to an S3 bucket.

## Results
The results of the benchmark will be saved in the specified S3 bucket under the `benchmark_results` directory.

## License
This project is licensed under the MIT License.
```

kubectl create secret docker-registry ghcr-secret --docker-server=ghcr.io --docker-username=narden91 --docker-password=$GITHUB_PAT --docker-email=eminik2006@gmail.com