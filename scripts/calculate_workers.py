#!/usr/bin/env python3
"""Calculate optimal worker count for Placement360 backend."""
import multiprocessing
import psutil

def calculate_optimal_workers():
    """Calculate recommended worker count."""
    cpu_count = multiprocessing.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024 ** 3)
    
    # Standard formula: (2 x CPU cores) + 1
    standard_workers = (2 * cpu_count) + 1
    
    # Memory-based limit (assume 256MB per worker)
    memory_based_workers = int(memory_gb / 0.256)
    
    # Cap at 8 workers for Placement360
    recommended_workers = min(standard_workers, memory_based_workers, 8)
    
    print("=" * 70)
    print("WORKER CALCULATION FOR PLACEMENT360 BACKEND")
    print("=" * 70)
    print(f"CPU Cores: {cpu_count}")
    print(f"Total Memory: {memory_gb:.2f} GB")
    print(f"Available Memory: {psutil.virtual_memory().available / (1024 ** 3):.2f} GB")
    print("-" * 70)
    print(f"Standard Formula (2 x CPU + 1): {standard_workers} workers")
    print(f"Memory-Based Limit (256MB/worker): {memory_based_workers} workers")
    print(f"Recommended for Placement360: {recommended_workers} workers")
    print("=" * 70)
    print()
    print("Update your configuration:")
    print(f"  uvicorn_config.py: workers = {recommended_workers}")
    print(f"  scripts/prod_server.sh: --workers {recommended_workers}")
    print(f"  .env: WORKERS={recommended_workers}")
    print("=" * 70)
    
    return recommended_workers

if __name__ == "__main__":
    calculate_optimal_workers()
