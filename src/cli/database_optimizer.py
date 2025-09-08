"""
Database Optimization Module

Handles database optimization and maintenance operations
for the Hocus Pocus terminal interface.

Author: Programmer-5090
Project: Hocus Pocus
"""

from src.core.engine import Engine
from typing import Dict, Any


def check_and_optimize_database(shazam_engine: Engine) -> None:
    """
    Check if database optimization is needed and perform it automatically.
    
    This function ensures the database is always in an optimized state by
    checking for binary blob data and converting it to proper integers
    for better performance and storage efficiency.
    
    Args:
        shazam_engine: Initialized Engine instance.
    """
    print("Checking database optimization status...")
    
    db_manager = shazam_engine.db_manager
    
    # Check if optimization is needed
    if db_manager.needs_optimization():
        print("Database optimization needed - found binary blob data")
        
        # Get current database size info
        size_info = db_manager.get_database_size_info()
        print(f"Current database size: {size_info['size_mb']:.1f} MB ({size_info['fingerprint_count']:,} fingerprints)")
        
        # Ask user if they want to optimize now
        try:
            choice = input("\nWould you like to optimize the database now? This will improve performance and reduce size. (y/n): ").strip().lower()
            
            if choice in ['y', 'yes']:
                print("\n" + "=" * 60)
                print("STARTING AUTOMATIC DATABASE OPTIMIZATION")
                print("=" * 60)
                
                # Perform optimization
                optimization_result = db_manager.optimize_database()
                
                if optimization_result['optimized']:
                    print("\n" + "=" * 60)
                    print("DATABASE OPTIMIZATION COMPLETE!")
                    print("=" * 60)
                    print(f"Optimization Results:")
                    print(f"   • Converted fingerprints: {optimization_result['converted_fingerprints']:,}")
                    print(f"   • Size before: {optimization_result['size_before'] / (1024*1024):.1f} MB")
                    print(f"   • Size after: {optimization_result['size_after'] / (1024*1024):.1f} MB")
                    print(f"   • Space saved: {optimization_result['size_reduction'] / (1024*1024):.1f} MB")
                    print(f"   • Size reduction: {optimization_result['reduction_percent']:.1f}%")
                    print("Database is now optimized for better performance!")
                    print("=" * 60)
                else:
                    print(f"Optimization not performed: {optimization_result.get('reason', 'Unknown reason')}")
            else:
                print("Skipping database optimization. You can run it later if needed.")
                
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping database optimization.")
    else:
        print("Database is already optimized!")
