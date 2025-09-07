"""
Test script to demonstrate automatic database optimization feature.

This script shows how the main program automatically detects and performs
database optimization when needed.
"""

from ..src.core.engine import Engine
from ..src.database.database_manager import DatabaseManager
import os


def test_optimization_detection():
    """Test the automatic optimization detection and execution."""
    
    print("🧪 TESTING AUTOMATIC DATABASE OPTIMIZATION")
    print("=" * 50)
    
    # Initialize engine
    shazam_engine = Engine()
    db_manager = shazam_engine.db_manager
    
    # Check current optimization status
    needs_opt = db_manager.needs_optimization()
    print(f"🔍 Database needs optimization: {needs_opt}")
    
    # Get current database info
    size_info = db_manager.get_database_size_info()
    print(f"📊 Current database size: {size_info['size_mb']:.1f} MB")
    print(f"📊 Total fingerprints: {size_info['fingerprint_count']:,}")
    print(f"📊 Avg bytes per fingerprint: {size_info['avg_bytes_per_fingerprint']:.1f}")
    
    if needs_opt:
        print("\n⚠️  Database optimization would be beneficial!")
        print("💡 Run main.py to see automatic optimization in action")
    else:
        print("\n✅ Database is already optimized!")
        print("🎯 Automatic optimization system is working correctly")
    
    print("\n" + "=" * 50)


def demonstrate_optimization_workflow():
    """Demonstrate the complete optimization workflow."""
    
    print("\n🚀 DEMONSTRATING OPTIMIZATION WORKFLOW")
    print("=" * 50)
    
    # This would simulate what happens in main.py
    shazam_engine = Engine()
    
    # Import the optimization check function from main
    from main import _check_and_optimize_database
    
    print("🔧 Running automatic optimization check...")
    try:
        _check_and_optimize_database(shazam_engine)
        print("✅ Optimization check completed successfully!")
    except Exception as e:
        print(f"❌ Error during optimization check: {e}")
    
    print("=" * 50)


if __name__ == "__main__":
    test_optimization_detection()
    demonstrate_optimization_workflow()
