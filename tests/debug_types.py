#!/usr/bin/env python3
"""
Data Type Debug Script

This script investigates the exact data type issue preventing fingerprint matching.
"""

import sqlite3
import numpy as np

def debug_data_types():
    """Debug the data type compatibility issue."""
    
    print("🔍 DEBUGGING DATA TYPE COMPATIBILITY")
    print("=" * 50)
    
    conn = sqlite3.connect("shazam_clone.db")
    cursor = conn.cursor()
    
    # Get a specific fingerprint from database
    cursor.execute("SELECT f_anchor, f_target, delta_t FROM Fingerprints WHERE song_id = 1 LIMIT 1")
    db_result = cursor.fetchone()
    f_anchor_db, f_target_db, delta_t_db = db_result
    
    print(f"📊 Database values:")
    print(f"   f_anchor: {f_anchor_db} (type: {type(f_anchor_db)})")
    print(f"   f_target: {f_target_db} (type: {type(f_target_db)})")
    print(f"   delta_t: {delta_t_db} (type: {type(delta_t_db)})")
    
    # Create numpy versions (like what comes from fingerprint generation)
    f_anchor_np = np.int64(f_anchor_db)
    f_target_np = np.int64(f_target_db)
    delta_t_np = np.int64(delta_t_db)
    
    print(f"\n📊 NumPy int64 versions:")
    print(f"   f_anchor: {f_anchor_np} (type: {type(f_anchor_np)})")
    print(f"   f_target: {f_target_np} (type: {type(f_target_np)})")
    print(f"   delta_t: {delta_t_np} (type: {type(delta_t_np)})")
    
    # Test exact matching with database types
    print(f"\n🔍 Testing exact matching with database types...")
    cursor.execute('''
        SELECT COUNT(*) FROM Fingerprints
        WHERE f_anchor=? AND f_target=? AND delta_t=?
    ''', (f_anchor_db, f_target_db, delta_t_db))
    count_db = cursor.fetchone()[0]
    print(f"   Using DB types: Found {count_db} matches")
    
    # Test matching with numpy types
    print(f"\n🔍 Testing matching with NumPy types...")
    cursor.execute('''
        SELECT COUNT(*) FROM Fingerprints
        WHERE f_anchor=? AND f_target=? AND delta_t=?
    ''', (f_anchor_np, f_target_np, delta_t_np))
    count_np = cursor.fetchone()[0]
    print(f"   Using NumPy types: Found {count_np} matches")
    
    # Test matching with Python int conversion
    print(f"\n🔍 Testing matching with Python int conversion...")
    cursor.execute('''
        SELECT COUNT(*) FROM Fingerprints
        WHERE f_anchor=? AND f_target=? AND delta_t=?
    ''', (int(f_anchor_np), int(f_target_np), int(delta_t_np)))
    count_int = cursor.fetchone()[0]
    print(f"   Using Python int: Found {count_int} matches")
    
    # Test type compatibility
    print(f"\n🔍 Testing type compatibility:")
    print(f"   DB int == NumPy int64: {f_anchor_db == f_anchor_np}")
    print(f"   DB int == Python int: {f_anchor_db == int(f_anchor_np)}")
    print(f"   NumPy int64 == Python int: {f_anchor_np == int(f_anchor_np)}")
    
    # Check what SQLite actually stores
    print(f"\n🔍 Checking SQLite type affinity:")
    cursor.execute("PRAGMA table_info(Fingerprints)")
    schema = cursor.fetchall()
    for col in schema:
        if col[1] in ['f_anchor', 'f_target', 'delta_t']:
            print(f"   {col[1]}: declared as {col[2]}")
    
    conn.close()

if __name__ == "__main__":
    debug_data_types()
