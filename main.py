from matrix_helper import MatrixOperations
from datetime import datetime
import os


def save_results(results, device_info):
    """
    Save benchmark results to a file in the results directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.getenv('RESULTS_DIR', 'results')
    filename = os.path.join(results_dir, f"matrix_multiplication_benchmark_{timestamp}.txt")
    
    with open(filename, 'w') as f:
        # Write header with device information
        f.write("Matrix Multiplication Benchmark Results\n")
        f.write("=====================================\n")
        f.write("\nDevice Information:\n")
        for key, value in device_info.items():
            f.write(f"{key}: {value}\n")
        
        # Write benchmark results
        f.write("\nBenchmark Results:\n")
        f.write("=====================================\n")
        f.write(f"{'Matrix Size':^12} | {'CPU Time (s)':^12} | {'GPU Time (s)':^12} | {'Speedup':^12}\n")
        f.write("-" * 55 + "\n")
        
        for result in results:
            gpu_time = f"{result['gpu_time']:.6f}" if result['gpu_time'] is not None else "N/A"
            speedup = f"{result['speedup']:.2f}x" if result['speedup'] is not None else "N/A"
            
            f.write(f"{result['size']:^12} | {result['cpu_time']:^12.6f} | {gpu_time:^12} | {speedup:^12}\n")
    
    return filename


def main():
    ops = MatrixOperations()
    
    sizes = [1000, 2000, 3000]
    
    print("Starting Matrix Multiplication Benchmark...")
    print("Testing matrix sizes:", sizes)
    
    results, device_info = ops.run_comparison(sizes)
    
    filename = save_results(results, device_info)
    
    print(f"\nBenchmark complete! Results saved to: {filename}")
    
    print("\nSummary:")
    print("-" * 55)
    print(f"{'Matrix Size':^12} | {'CPU Time (s)':^12} | {'GPU Time (s)':^12} | {'Speedup':^12}")
    print("-" * 55)
    for result in results:
        gpu_time = f"{result['gpu_time']:.6f}" if result['gpu_time'] is not None else "N/A"
        speedup = f"{result['speedup']:.2f}x" if result['speedup'] is not None else "N/A"
        print(f"{result['size']:^12} | {result['cpu_time']:^12.6f} | {gpu_time:^12} | {speedup:^12}")


if __name__ == "__main__":
    main()