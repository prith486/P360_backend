#!/usr/bin/env python3
"""
Calculate optimal database connection pool settings for Placement360.
Based on concurrent users, worker count, and database limits.
"""

def calculate_pool_settings(
    concurrent_users: int,
    workers: int,
    supabase_max_connections: int = 60  # Free tier limit
):
    """Calculate optimal pool settings."""
    
    # Reserve connections for background tasks and migrations
    reserved_connections = 5
    available_connections = supabase_max_connections - reserved_connections
    connections_per_worker = available_connections // workers
    
    # Split into pool_size (always available) and max_overflow (on-demand)
    # Ratio: 40% pool_size, 60% max_overflow
    pool_size = max(int(connections_per_worker * 0.4), 5)
    max_overflow = max(int(connections_per_worker * 0.6), 10)
    
    # Calculate capacity
    total_connections = (pool_size + max_overflow) * workers
    requests_per_second = total_connections * 10  # Assume 100ms per request
    
    # Check if we can handle concurrent users (20% active at once)
    active_requests = concurrent_users * 0.2
    
    return {
        "concurrent_users": concurrent_users,
        "workers": workers,
        "database_limit": supabase_max_connections,
        "recommended": {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": 30,
            "pool_recycle": 3600
        },
        "capacity": {
            "total_connections": total_connections,
            "requests_per_second": requests_per_second,
            "can_handle_load": total_connections >= active_requests
        }
    }

if __name__ == "__main__":
    print("=" * 70)
    print("DATABASE CONNECTION POOL CALCULATOR - PLACEMENT360")
    print("=" * 70)
    print()
    
    # Development scenario
    print("Scenario 1: Development (1 worker, 100 users)")
    print("-" * 50)
    result = calculate_pool_settings(100, 1)
    print(f"Recommended: pool_size={result['recommended']['pool_size']}, max_overflow={result['recommended']['max_overflow']}")
    print(f"Capacity: {result['capacity']['total_connections']} total connections, {result['capacity']['requests_per_second']} req/sec")
    print()
    
    # Production scenario
    print("Scenario 2: Production (4 workers, 5000 users)")
    # Note: For production with 5000 users, we'd need more than the free tier limit (60 connections).
    # Assuming Supabase Pro (pooler enabled) or a larger limit for the calculation.
    # But sticking to the script logic provided by user which uses default 60 if not specified, 
    # but let's see what happens. The user provided code uses default 60.
    # Wait, the prompt code calls `calculate_pool_settings(5000, 4)`.
    # Let's inspect the logic. 
    # available = 60 - 5 = 55.
    # per_worker = 55 // 4 = 13.
    # pool_size = max(13*0.4, 5) = max(5.2, 5) = 5.
    # max_overflow = max(13*0.6, 10) = max(7.8, 10) = 10.
    # total = (5+10)*4 = 60.
    # req/sec = 600.
    # active = 5000 * 0.2 = 1000.
    # 60 >= 1000 is False.
    # So it will say "No". which is correct for free tier.
    
    print("-" * 50)
    result = calculate_pool_settings(5000, 4)
    print(f"Recommended: pool_size={result['recommended']['pool_size']}, max_overflow={result['recommended']['max_overflow']}")
    print(f"Capacity: {result['capacity']['total_connections']} total connections, {result['capacity']['requests_per_second']} req/sec")
    print(f"Can handle load: {'✓ Yes' if result['capacity']['can_handle_load'] else '✗ No'}")
    
    print("=" * 70)
    # The prompt actually includes these lines in the main block in the request description.
    # I should copy the request exactly.
    print("Update your .env file with recommended settings:")
    print(f"DB_POOL_SIZE={result['recommended']['pool_size']}")
    print(f"DB_MAX_OVERFLOW={result['recommended']['max_overflow']}")
    print("=" * 70)
