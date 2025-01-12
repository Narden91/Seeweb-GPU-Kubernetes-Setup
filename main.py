import sys

sys.dont_write_bytecode = True

from config.s3_config_handler import ConfigHandler
from s3_operations.s3_operations import S3Operations
from benchmark_operations.benchmark_operations import BenchmarkOperations
from cli_operations.cli_operations import CLIOperations
from rich.console import Console


console = Console()


def main():
    """Main function to run the matrix multiplication benchmark"""
    # Initialize operations
    cli_ops = CLIOperations()
    sizes, source = cli_ops.get_matrix_sizes()
    
    # Initialize configuration handler for S3 access
    config = ConfigHandler()
    
    # Initialize S3 operations
    s3_ops = S3Operations(config.get_aws_credentials(), config.s3_bucket)
    
    # Display configuration
    cli_ops.display_configuration(sizes, source)
    
    # Display file count in S3 bucket
    txt_count = s3_ops.count_txt_files()
    console.print(f"\n[cyan]Number of existing benchmark files:[/] {txt_count}")
    
    # Run benchmark
    benchmark_ops = BenchmarkOperations()
    console.print("\n[bold cyan]Starting benchmark...[/]")
    results, device_info = benchmark_ops.run_comparison(sizes)
    
    # Save and display results
    filename = s3_ops.save_results(results, device_info)
    console.print(f"\n[green]Benchmark complete! Results saved to:[/] {filename}")
    
    cli_ops.display_results(results)


if __name__ == "__main__":
    main()