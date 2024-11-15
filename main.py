from matrix_helper import MatrixOperations
from datetime import datetime
import os
from config.config import config
import sys
import boto3
import io
from rich import print as rprint
from rich.console import Console

console = Console()


sys.dont_write_bytecode = True


def save_results(results, device_info, s3_client, bucket_name):
    """
    Save benchmark results to a file in S3 bucket
    
    Args:
    - results: List of dictionaries containing benchmark results
    - device_info: Dictionary containing information about the device
    - s3_client: Boto3 S3 client
    - bucket_name: Name of the S3 bucket
    
    Returns:
    - URL of the file in S3
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"matrix_multiplication_benchmark_{timestamp}.txt"
    
    # Create string buffer to write results
    buffer = io.StringIO()
    
    # Write header with device information
    buffer.write("Matrix Multiplication Benchmark Results\n")
    buffer.write("=====================================\n")
    buffer.write("\nDevice Information:\n")
    for key, value in device_info.items():
        buffer.write(f"{key}: {value}\n")
    
    # Write benchmark results
    buffer.write("\nBenchmark Results:\n")
    buffer.write("=====================================\n")
    buffer.write(f"{'Matrix Size':^12} | {'CPU Time (s)':^12} | {'GPU Time (s)':^12} | {'Speedup':^12}\n")
    buffer.write("-" * 55 + "\n")
    
    for result in results:
        gpu_time = f"{result['gpu_time']:.6f}" if result['gpu_time'] is not None else "N/A"
        speedup = f"{result['speedup']:.2f}x" if result['speedup'] is not None else "N/A"
        
        buffer.write(f"{result['size']:^12} | {result['cpu_time']:^12.6f} | {gpu_time:^12} | {speedup:^12}\n")
    
    # Upload to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"benchmark_results/{filename}",
        Body=buffer.getvalue()
    )
    
    buffer.close()
    return f"s3://{bucket_name}/benchmark_results/{filename}"


def main():
    """
    Main function to run the matrix multiplication benchmark
    
    This function will:
    - Initialize the MatrixOperations class
    - Run the benchmark for different matrix sizes
    - Save the results to a file in S3
    """
    credentials = config.get_aws_credentials()
    s3_client = boto3.client(
        's3',
        endpoint_url=credentials['aws_endpoint_url'],
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key']
    )
    
    ops = MatrixOperations()
    sizes = [1000, 2000, 3000]
    
    console.log("Starting Matrix Multiplication Benchmark...")
    console.log("Testing matrix sizes:", sizes)
    
    results, device_info = ops.run_comparison(sizes)
    
    filename = save_results(results, device_info, s3_client, config.s3_bucket)
    
    console.log(f"\nBenchmark complete! Results saved to: {filename}")
    
    console.log("\nSummary:")
    console.log("-" * 55)
    console.log(f"{'Matrix Size':^12} | {'CPU Time (s)':^12} | {'GPU Time (s)':^12} | {'Speedup':^12}")
    console.log("-" * 55)
    for result in results:
        gpu_time = f"{result['gpu_time']:.6f}" if result['gpu_time'] is not None else "N/A"
        speedup = f"{result['speedup']:.2f}x" if result['speedup'] is not None else "N/A"
        console.log(f"{result['size']:^12} | {result['cpu_time']:^12.6f} | {gpu_time:^12} | {speedup:^12}")


if __name__ == "__main__":
    main()
