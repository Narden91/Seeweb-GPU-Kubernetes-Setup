import sys
import argparse

sys.dont_write_bytecode = True

from matrix_helper import MatrixOperations
from datetime import datetime
import os
from config.config import config
import boto3
import io
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.style import Style

console = Console()


def parse_matrix_sizes(sizes_str):
    """
    Parse matrix sizes string into a list of integers
    
    Args:
    - sizes_str: Comma-separated string of matrix sizes
    
    Returns:
    - List of integers representing matrix sizes
    """
    try:
        return [int(size.strip()) for size in sizes_str.split(',')]
    except ValueError:
        raise argparse.ArgumentTypeError("Matrix sizes must be comma-separated integers")

def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
    - Parsed argument namespace
    """
    parser = argparse.ArgumentParser(description='Matrix multiplication benchmark')
    parser.add_argument(
        '--matrix-sizes',
        type=parse_matrix_sizes,
        help='Comma-separated list of matrix sizes (e.g., 1000,2000,3000)'
    )
    return parser.parse_args()

def get_matrix_sizes():
    """
    Get matrix sizes from command line or environment variable
    
    Returns:
    - tuple: (list of sizes, source of sizes)
    """
    args = parse_arguments()
    
    # Check command line arguments first
    if args.matrix_sizes is not None:
        return args.matrix_sizes, "command line"
    
    # Check environment variable
    env_sizes = os.getenv('MATRIX_SIZES')
    if env_sizes:
        return parse_matrix_sizes(env_sizes), "environment variable"
    
    # Use default values if neither is provided
    default_sizes = [1000, 2000, 3000]
    return default_sizes, "default values"

def save_results(results, device_info, s3_client, bucket_name):
    """
    Save benchmark results to a file in S3 bucket
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"matrix_multiplication_benchmark_{timestamp}.txt"
    
    buffer = io.StringIO()
    
    buffer.write("Matrix Multiplication Benchmark Results\n")
    buffer.write("=====================================\n")
    buffer.write("\nDevice Information:\n")
    for key, value in device_info.items():
        buffer.write(f"{key}: {value}\n")
    
    buffer.write("\nBenchmark Results:\n")
    buffer.write("=====================================\n")
    buffer.write(f"{'Matrix Size':^12} | {'CPU Time (s)':^12} | {'GPU Time (s)':^12} | {'Speedup':^12}\n")
    buffer.write("-" * 55 + "\n")
    
    for result in results:
        gpu_time = f"{result['gpu_time']:.6f}" if result['gpu_time'] is not None else "N/A"
        speedup = f"{result['speedup']:.2f}x" if result['speedup'] is not None else "N/A"
        buffer.write(f"{result['size']:^12} | {result['cpu_time']:^12.6f} | {gpu_time:^12} | {speedup:^12}\n")
    
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
    """
    # Get matrix sizes and their source
    sizes, source = get_matrix_sizes()
    
    # Print configuration information using rich
    console.print(Panel(
        f"[bold green]Matrix Multiplication Benchmark Configuration[/]\n\n"
        f"[yellow]Matrix sizes source:[/] {source}\n"
        f"[yellow]Matrix sizes:[/] {', '.join(map(str, sizes))}",
        title="Configuration",
        style="blue"
    ))
    
    credentials = config.get_aws_credentials()
    s3_client = boto3.client(
        's3',
        endpoint_url=credentials['aws_endpoint_url'],
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key']
    )
    
    ops = MatrixOperations()
    
    console.print("\n[bold cyan]Starting benchmark...[/]")
    results, device_info = ops.run_comparison(sizes)
    
    filename = save_results(results, device_info, s3_client, config.s3_bucket)
    
    console.print(f"\n[green]Benchmark complete! Results saved to:[/] {filename}")
    
    # Print results table
    console.print("\n[bold]Summary:[/]")
    console.print("─" * 55)
    console.print(f"{'Matrix Size':^12} | {'CPU Time (s)':^12} | {'GPU Time (s)':^12} | {'Speedup':^12}")
    console.print("─" * 55)
    
    for result in results:
        gpu_time = f"{result['gpu_time']:.6f}" if result['gpu_time'] is not None else "N/A"
        speedup = f"{result['speedup']:.2f}x" if result['speedup'] is not None else "N/A"
        
        # Color-code the speedup values
        if result['speedup'] and result['speedup'] > 2:
            speedup_color = "bright_green"
        elif result['speedup'] and result['speedup'] > 1:
            speedup_color = "green"
        else:
            speedup_color = "yellow"
            
        console.print(
            f"{result['size']:^12} | "
            f"{result['cpu_time']:^12.6f} | "
            f"{gpu_time:^12} | "
            f"[{speedup_color}]{speedup:^12}[/]"
        )


if __name__ == "__main__":
    main()