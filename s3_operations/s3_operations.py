import boto3
import io
from datetime import datetime
from rich.console import Console

console = Console()

class S3Operations:
    def __init__(self, credentials, bucket_name):
        """
        Initialize S3 operations with credentials and bucket name
        
        Args:
        - credentials: Dict containing AWS credentials
        - bucket_name: Name of the S3 bucket
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            endpoint_url=credentials['aws_endpoint_url'],
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key']
        )

    def count_txt_files(self):
        """
        Count the number of .txt files in the benchmark_results folder
        
        Returns:
        - Integer count of .txt files
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='benchmark_results/'
            )
            
            if 'Contents' not in response:
                return 0
                
            txt_files = [obj for obj in response['Contents'] 
                        if obj['Key'].endswith('.txt')]
            return len(txt_files)
        except Exception as e:
            console.print(f"[red]Error counting txt files: {str(e)}[/]")
            return 0

    def save_results(self, results, device_info):
        """
        Save benchmark results to a file in S3 bucket
        
        Args:
        - results: Benchmark results to save
        - device_info: Information about the device used
        
        Returns:
        - S3 URI of saved file
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
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=f"benchmark_results/{filename}",
            Body=buffer.getvalue()
        )
        
        buffer.close()
        return f"s3://{self.bucket_name}/benchmark_results/{filename}"