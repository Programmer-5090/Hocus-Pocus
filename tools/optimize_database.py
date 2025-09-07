#!/usr/bin/env python3
"""
Database Optimization Script - Shazam Clone Database Size Reduction

This script optimizes the Shazam clone database by:
1. Converting binary blob fingerprints to proper integers
2. Removing duplicate indices 
3. Vacuuming the database to reclaim space
4. Analyzing space savings

The current issue: Fingerprints are stored as 8-byte binary blobs instead of
variable-length integers, causing massive space inefficiency.
"""

import sqlite3
import os
import shutil
from typing import Tuple
import struct

def backup_database(db_path: str) -> str:
    """Create a backup of the original database."""
    backup_path = f"{db_path}.backup"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def analyze_fingerprint_data(db_path: str) -> None:
    """Analyze the current fingerprint storage format."""
    print("\n🔍 Analyzing current fingerprint storage format...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get a sample of fingerprint data
    cursor.execute("SELECT f_anchor, f_target, delta_t, t_anchor FROM Fingerprints LIMIT 5")
    samples = cursor.fetchall()
    
    print("📊 Sample fingerprint data (raw):")
    for i, (f_anchor, f_target, delta_t, t_anchor) in enumerate(samples):
        print(f"   Row {i+1}:")
        print(f"      f_anchor: {f_anchor} (type: {type(f_anchor)}, len: {len(f_anchor) if isinstance(f_anchor, bytes) else 'N/A'})")
        print(f"      f_target: {f_target} (type: {type(f_target)}, len: {len(f_target) if isinstance(f_target, bytes) else 'N/A'})")
        print(f"      delta_t:  {delta_t} (type: {type(delta_t)}, len: {len(delta_t) if isinstance(delta_t, bytes) else 'N/A'})")
        print(f"      t_anchor: {t_anchor} (type: {type(t_anchor)}, len: {len(t_anchor) if isinstance(t_anchor, bytes) else 'N/A'})")
        
        # Try to decode as integers
        if isinstance(f_anchor, bytes):
            try:
                f_anchor_int = struct.unpack('<Q', f_anchor)[0]  # Little-endian uint64
                f_target_int = struct.unpack('<Q', f_target)[0]
                delta_t_int = struct.unpack('<Q', delta_t)[0]
                t_anchor_int = struct.unpack('<Q', t_anchor)[0]
                print(f"      Decoded: f_anchor={f_anchor_int}, f_target={f_target_int}, delta_t={delta_t_int}, t_anchor={t_anchor_int}")
            except Exception as e:
                print(f"      ❌ Decode error: {e}")
    
    conn.close()

def optimize_database(db_path: str) -> Tuple[float, float]:
    """Optimize the database by converting binary data to integers."""
    
    print(f"\n🔧 Starting database optimization...")
    
    # Get original size
    original_size = os.path.getsize(db_path) / (1024 * 1024)
    print(f"📊 Original size: {original_size:.2f} MB")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Create a new optimized fingerprints table
        print("🔨 Creating optimized fingerprints table...")
        cursor.execute("""
            CREATE TABLE Fingerprints_Optimized (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER NOT NULL,
                f_anchor INTEGER NOT NULL,
                f_target INTEGER NOT NULL, 
                delta_t INTEGER NOT NULL,
                t_anchor INTEGER NOT NULL,
                FOREIGN KEY (song_id) REFERENCES Songs (song_id)
            )
        """)
        
        # Step 2: Convert and copy data
        print("🔄 Converting binary data to integers...")
        cursor.execute("SELECT COUNT(*) FROM Fingerprints")
        total_rows = cursor.fetchone()[0]
        print(f"📊 Processing {total_rows:,} fingerprint records...")
        
        # Process in batches to avoid memory issues
        batch_size = 10000
        processed = 0
        
        cursor.execute("SELECT id, song_id, f_anchor, f_target, delta_t, t_anchor FROM Fingerprints")
        
        insert_cursor = conn.cursor()
        batch_data = []
        
        for row in cursor:
            row_id, song_id, f_anchor, f_target, delta_t, t_anchor = row
            
            try:
                # Convert binary data to integers
                if isinstance(f_anchor, bytes):
                    f_anchor_int = struct.unpack('<Q', f_anchor)[0]
                    f_target_int = struct.unpack('<Q', f_target)[0] 
                    delta_t_int = struct.unpack('<Q', delta_t)[0]
                    t_anchor_int = struct.unpack('<Q', t_anchor)[0]
                else:
                    # Already integers
                    f_anchor_int = f_anchor
                    f_target_int = f_target
                    delta_t_int = delta_t
                    t_anchor_int = t_anchor
                
                batch_data.append((song_id, f_anchor_int, f_target_int, delta_t_int, t_anchor_int))
                
                if len(batch_data) >= batch_size:
                    insert_cursor.executemany(
                        "INSERT INTO Fingerprints_Optimized (song_id, f_anchor, f_target, delta_t, t_anchor) VALUES (?, ?, ?, ?, ?)",
                        batch_data
                    )
                    conn.commit()
                    processed += len(batch_data)
                    batch_data = []
                    print(f"   ✅ Processed {processed:,}/{total_rows:,} records ({(processed/total_rows)*100:.1f}%)")
                    
            except Exception as e:
                print(f"   ❌ Error processing row {row_id}: {e}")
                continue
        
        # Insert remaining batch
        if batch_data:
            insert_cursor.executemany(
                "INSERT INTO Fingerprints_Optimized (song_id, f_anchor, f_target, delta_t, t_anchor) VALUES (?, ?, ?, ?, ?)",
                batch_data
            )
            conn.commit()
            processed += len(batch_data)
        
        print(f"✅ Converted {processed:,} fingerprint records")
        
        # Step 3: Replace old table with optimized one
        print("🔄 Replacing old table with optimized version...")
        cursor.execute("DROP TABLE Fingerprints")
        cursor.execute("ALTER TABLE Fingerprints_Optimized RENAME TO Fingerprints")
        
        # Step 4: Recreate indices (but remove duplicates)
        print("🔨 Creating optimized indices...")
        
        # Primary index for matching
        cursor.execute("""
            CREATE INDEX idx_fingerprint_lookup 
            ON Fingerprints (f_anchor, f_target, delta_t)
        """)
        
        # Index for song-based queries
        cursor.execute("""
            CREATE INDEX idx_song_fingerprints 
            ON Fingerprints (song_id)
        """)
        
        # Step 5: Vacuum database to reclaim space
        print("🧹 Vacuuming database to reclaim space...")
        cursor.execute("VACUUM")
        
        conn.commit()
        print("✅ Database optimization completed!")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    # Get new size
    new_size = os.path.getsize(db_path) / (1024 * 1024)
    space_saved = original_size - new_size
    savings_percent = (space_saved / original_size) * 100
    
    print(f"\n📊 Optimization Results:")
    print(f"   📉 Original size: {original_size:.2f} MB")
    print(f"   📈 New size: {new_size:.2f} MB")
    print(f"   💾 Space saved: {space_saved:.2f} MB ({savings_percent:.1f}%)")
    
    return original_size, new_size

def verify_optimization(db_path: str) -> None:
    """Verify that the optimization worked correctly."""
    print(f"\n✅ Verifying optimization...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check data types
        cursor.execute("SELECT f_anchor, f_target, delta_t, t_anchor FROM Fingerprints LIMIT 3")
        samples = cursor.fetchall()
        
        print("📊 Sample optimized data:")
        for i, (f_anchor, f_target, delta_t, t_anchor) in enumerate(samples):
            print(f"   Row {i+1}: f_anchor={f_anchor} ({type(f_anchor)}), f_target={f_target} ({type(f_target)})")
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM Fingerprints")
        fingerprint_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Songs")
        song_count = cursor.fetchone()[0]
        
        print(f"📊 Data integrity check:")
        print(f"   🎵 Songs: {song_count}")
        print(f"   🔑 Fingerprints: {fingerprint_count:,}")
        
        # Test a quick query
        cursor.execute("SELECT song_id, COUNT(*) FROM Fingerprints GROUP BY song_id LIMIT 5")
        song_fingerprints = cursor.fetchall()
        print(f"📊 Fingerprints per song (sample):")
        for song_id, count in song_fingerprints:
            print(f"   Song {song_id}: {count:,} fingerprints")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
    finally:
        conn.close()

def main():
    """Main optimization workflow."""
    db_path = "shazam_clone.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return
    
    print("🚀 Shazam Clone Database Optimization")
    print("=" * 50)
    
    # Analyze current state
    analyze_fingerprint_data(db_path)
    
    # Create backup
    backup_path = backup_database(db_path)
    
    try:
        # Optimize database
        original_size, new_size = optimize_database(db_path)
        
        # Verify optimization
        verify_optimization(db_path)
        
        print(f"\n🎉 Optimization completed successfully!")
        print(f"💾 Backup available at: {backup_path}")
        
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        print(f"🔄 Restoring from backup...")
        shutil.copy2(backup_path, db_path)
        print(f"✅ Database restored from backup")

if __name__ == "__main__":
    main()
