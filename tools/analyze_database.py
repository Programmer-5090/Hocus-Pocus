#!/usr/bin/env python3
"""
Database Analysis Script - Shazam Clone Database Size Investigation

This script analyzes the structure and size of the Shazam clone database
to identify optimization opportunities and understand storage usage.
"""

import sqlite3
import os

def analyze_database():
    """Analyze the database structure and provide optimization recommendations."""
    
    db_path = "shazam_clone.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return
    
    # Get database file size
    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"📊 Database file size: {db_size_mb:.2f} MB")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📋 Found {len(tables)} tables:")
        
        total_rows = 0
        for table_name, in tables:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            total_rows += row_count
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            
            print(f"\n🔍 Table: {table_name}")
            print(f"   📊 Rows: {row_count:,}")
            print(f"   📋 Schema:")
            for column in schema:
                col_id, name, data_type, not_null, default, pk = column
                print(f"      - {name}: {data_type}")
            
            # Sample a few rows to understand data
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                samples = cursor.fetchall()
                print(f"   📄 Sample data:")
                for i, sample in enumerate(samples):
                    print(f"      Row {i+1}: {sample}")
        
        print(f"\n📊 Total rows across all tables: {total_rows:,}")
        print(f"📐 Average size per row: {(db_size_mb * 1024 * 1024) / total_rows:.2f} bytes")
        
        # Check for indices
        print(f"\n🔍 Database indices:")
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
        indices = cursor.fetchall()
        for index_name, table_name, sql in indices:
            if index_name.startswith('sqlite_'):
                continue  # Skip system indices
            print(f"   📌 {index_name} on {table_name}")
            print(f"      SQL: {sql}")
        
        # Analyze database statistics
        print(f"\n📊 Database statistics:")
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        print(f"   📄 Page size: {page_size} bytes")
        
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        print(f"   📚 Page count: {page_count:,}")
        
        cursor.execute("PRAGMA freelist_count")
        free_pages = cursor.fetchone()[0]
        print(f"   🗑️  Free pages: {free_pages:,}")
        
        # Calculate space efficiency
        used_space = (page_count - free_pages) * page_size / (1024 * 1024)
        free_space = free_pages * page_size / (1024 * 1024)
        print(f"   💾 Used space: {used_space:.2f} MB")
        print(f"   🗑️  Free space: {free_space:.2f} MB")
        print(f"   📈 Space efficiency: {(used_space / db_size_mb) * 100:.1f}%")
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_database()
