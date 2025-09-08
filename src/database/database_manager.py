"""
Database management module for audio fingerprint storage and retrieval.

This module provides a complete database abstraction layer for storing
song metadata and audio fingerprints, as well as performing efficient
fingerprint matching for audio identification.

Author: Hocus Pocus Project
Version: 1.0
"""

import sqlite3
import struct
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, DefaultDict


class DatabaseManager:
    """
    Manages SQLite database operations for audio fingerprint storage and matching.
    
    This class handles all database interactions including song storage,
    fingerprint indexing, and optimized query matching for audio identification.
    It provides a robust foundation for large-scale audio fingerprint databases.
    """
    
    def __init__(self, db_path: str = "data/shazam_clone.db"):
        """
        Initialize the database manager and ensure database schema exists.
        
        Args:
            db_path: Path to the SQLite database file. Will be created if it doesn't exist.
        """
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """
        Create database tables and indexes if they don't exist.
        
        This method sets up the complete database schema including:
        - Songs table for metadata storage
        - Fingerprints table for audio signatures
        - Optimized indexes for fast fingerprint matching
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create Songs table for metadata storage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Songs (
                    song_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT,
                    file_path TEXT,
                    duration REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create Fingerprints table for audio signature storage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id INTEGER NOT NULL,
                    f_anchor INTEGER NOT NULL,
                    f_target INTEGER NOT NULL,
                    delta_t INTEGER NOT NULL,
                    t_anchor INTEGER NOT NULL,
                    FOREIGN KEY (song_id) REFERENCES Songs(song_id) ON DELETE CASCADE
                )
            ''')
            
            # Create optimized index for fingerprint matching performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_fingerprint_lookup 
                ON Fingerprints (f_anchor, f_target, delta_t)
            ''')
            
            # Create index for song-based queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_song_fingerprints 
                ON Fingerprints (song_id)
            ''')
            
            conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a new database connection.
        
        Returns:
            SQLite connection object with row factory configured for easier data access.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def add_song(self, title: str, artist: str = None, file_path: str = None, 
                 duration: float = None) -> int:
        """
        Add a song to the database.
        
        Args:
            title: Song title
            artist: Artist name (optional)
            file_path: Path to the audio file (optional)
            duration: Song duration in seconds (optional)
            
        Returns:
            The song_id of the inserted song
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Songs (title, artist, file_path, duration)
                VALUES (?, ?, ?, ?)
            ''', (title, artist, file_path, duration))
            return cursor.lastrowid
    
    def add_fingerprints(self, song_id: int, fingerprints: List[Tuple[Tuple[int, int, int], int]]):
        """
        Add fingerprints for a song to the database.
        
        Args:
            song_id: ID of the song
            fingerprints: List of ((f_anchor, f_target, delta_t), t_anchor) tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            fingerprint_data = []
            for (f_anchor, f_target, delta_t), t_anchor in fingerprints:
                # Convert NumPy types to Python integers for SQLite compatibility
                fingerprint_data.append((
                    int(song_id), 
                    int(f_anchor), 
                    int(f_target), 
                    int(delta_t), 
                    int(t_anchor)
                ))
            
            cursor.executemany('''
                INSERT INTO Fingerprints (song_id, f_anchor, f_target, delta_t, t_anchor)
                VALUES (?, ?, ?, ?, ?)
            ''', fingerprint_data)
    
    def get_song_info(self, song_id: int) -> Optional[Dict]:
        """
        Get song information by ID.
        
        Args:
            song_id: ID of the song
            
        Returns:
            Dictionary with song information or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT song_id, title, artist, file_path, duration, created_at
                FROM Songs WHERE song_id = ?
            ''', (song_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'song_id': row[0],
                    'title': row[1],
                    'artist': row[2],
                    'file_path': row[3],
                    'duration': row[4],
                    'created_at': row[5]
                }
            return None
    
    def list_songs(self) -> List[Dict]:
        """
        List all songs in the database.
        
        Returns:
            List of dictionaries with song information
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT song_id, title, artist, file_path, duration, created_at
                FROM Songs ORDER BY created_at DESC
            ''')
            
            songs = []
            for row in cursor.fetchall():
                songs.append({
                    'song_id': row[0],
                    'title': row[1],
                    'artist': row[2],
                    'file_path': row[3],
                    'duration': row[4],
                    'created_at': row[5]
                })
            return songs
    
    def match_query(self, fingerprints_query: List[Tuple[Tuple[int, int, int], int]]) -> Tuple[Optional[int], Dict]:
        """
        Match query fingerprints against the database.
        
        Args:
            fingerprints_query: List of ((f_anchor, f_target, delta_t), t_anchor_query) tuples
            
        Returns:
            Tuple of (best_song_id, scores_dict)
        """
        scores = defaultdict(int)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for (f_anchor, f_target, delta_t), t_anchor_query in fingerprints_query:
                # Convert NumPy types to Python integers for SQLite compatibility
                f_anchor = int(f_anchor)
                f_target = int(f_target) 
                delta_t = int(delta_t)
                t_anchor_query = int(t_anchor_query)
                
                cursor.execute('''
                    SELECT song_id, t_anchor 
                    FROM Fingerprints
                    WHERE f_anchor=? AND f_target=? AND delta_t=?
                ''', (f_anchor, f_target, delta_t))

                matches = cursor.fetchall()
                for song_id, t_anchor_db in matches:
                    # Ensure database values are also integers
                    try:
                        if isinstance(t_anchor_db, bytes):
                            # Legacy handling for binary data (shouldn't occur after optimization)
                            if len(t_anchor_db) >= 4:
                                t_anchor_db = struct.unpack('<i', t_anchor_db[:4])[0]
                            else:
                                t_anchor_db = int.from_bytes(t_anchor_db, 'little')
                        else:
                            t_anchor_db = int(t_anchor_db)
                        
                        # Calculate time offset for this match
                        offset = t_anchor_db - t_anchor_query
                        scores[(song_id, offset)] += 1
                        
                    except (ValueError, struct.error) as e:
                        # Skip corrupted data
                        print(f"Warning: Skipping corrupted fingerprint data: {e}")
                        continue

        if scores:
            # Find the best match by maximum score
            best_match = max(scores.items(), key=lambda x: x[1])
            best_song_id = best_match[0][0]
            return best_song_id, dict(scores)
        else:
            return None, dict(scores)
    
    def get_match_details(self, song_id: int, scores: Dict) -> Dict:
        """
        Get detailed match information.
        
        Args:
            song_id: ID of the matched song
            scores: Scores dictionary from match_query
            
        Returns:
            Dictionary with match details
        """
        song_info = self.get_song_info(song_id)
        if not song_info:
            return {}
        
        # Find best offset and score for this song
        song_scores = [(offset, score) for (sid, offset), score in scores.items() if sid == song_id]
        if song_scores:
            best_offset, best_score = max(song_scores, key=lambda x: x[1])
            total_matches = sum(score for _, score in song_scores)
        else:
            best_offset, best_score, total_matches = 0, 0, 0
        
        return {
            'song_info': song_info,
            'best_offset': best_offset,
            'best_score': best_score,
            'total_matches': total_matches,
            'confidence': best_score / len(scores) if scores else 0
        }
    
    def needs_optimization(self) -> bool:
        """
        Check if the database needs optimization.
        
        This method detects if the fingerprints table contains binary blob data
        that should be converted to proper integers for better performance and
        smaller storage size.
        
        Returns:
            True if optimization is needed, False otherwise.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if we have any fingerprints
            cursor.execute("SELECT COUNT(*) FROM Fingerprints LIMIT 1")
            if cursor.fetchone()[0] == 0:
                return False
            
            # Sample a few records to check data types
            cursor.execute("SELECT f_anchor, f_target, delta_t, t_anchor FROM Fingerprints LIMIT 10")
            rows = cursor.fetchall()
            
            for row in rows:
                # Check if any values are stored as binary blobs
                for value in row:
                    if isinstance(value, bytes):
                        return True
            
            return False
    
    def is_optimized(self) -> bool:
        """
        Check if the database has been optimized (fingerprints stored as integers).
        
        Returns:
            True if database is optimized, False if it needs optimization.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if we have any fingerprints
            cursor.execute("SELECT COUNT(*) FROM Fingerprints LIMIT 1")
            if cursor.fetchone()[0] == 0:
                return True  # Empty database is considered optimized
            
            # Sample a few records to check data types
            cursor.execute("SELECT f_anchor, f_target, delta_t, t_anchor FROM Fingerprints LIMIT 5")
            rows = cursor.fetchall()
            
            for row in rows:
                # Check if any values are stored as binary blobs (unoptimized)
                for value in row:
                    if isinstance(value, bytes):
                        return False
            
            return True
    
    def optimize_database(self) -> Dict[str, any]:
        """
        Optimize the database by converting binary blob fingerprints to integers.
        
        This process converts fingerprint data from binary blob storage to
        proper integer storage, resulting in smaller database size and better
        query performance.
        
        Returns:
            Dictionary with optimization results including before/after sizes.
        """
        import os
        
        # Get database size before optimization
        size_before = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        print("Starting database optimization...")
        print("Converting binary fingerprint data to optimized integers...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total count for progress tracking
            cursor.execute("SELECT COUNT(*) FROM Fingerprints")
            total_fingerprints = cursor.fetchone()[0]
            
            if total_fingerprints == 0:
                return {
                    'optimized': False,
                    'reason': 'No fingerprints to optimize',
                    'size_before': size_before,
                    'size_after': size_before
                }
            
            print(f"Processing {total_fingerprints:,} fingerprints...")
            
            # Process in batches to avoid memory issues
            batch_size = 10000
            processed = 0
            converted = 0
            
            cursor.execute("SELECT id, f_anchor, f_target, delta_t, t_anchor FROM Fingerprints")
            
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                
                updates = []
                for fingerprint_id, f_anchor, f_target, delta_t, t_anchor in rows:
                    needs_update = False
                    new_values = []
                    
                    # Convert each field if it's binary data
                    for value in [f_anchor, f_target, delta_t, t_anchor]:
                        if isinstance(value, bytes):
                            needs_update = True
                            try:
                                if len(value) >= 4:
                                    converted_value = struct.unpack('<i', value[:4])[0]
                                else:
                                    converted_value = int.from_bytes(value, 'little')
                            except (struct.error, ValueError):
                                converted_value = 0  # Fallback for corrupted data
                            new_values.append(int(converted_value))
                        else:
                            new_values.append(int(value))
                    
                    if needs_update:
                        updates.append((new_values[0], new_values[1], new_values[2], new_values[3], fingerprint_id))
                        converted += 1
                
                # Apply updates if any
                if updates:
                    cursor.executemany('''
                        UPDATE Fingerprints 
                        SET f_anchor=?, f_target=?, delta_t=?, t_anchor=? 
                        WHERE id=?
                    ''', updates)
                
                processed += len(rows)
                
                # Show progress every 100k records
                if processed % 100000 == 0:
                    progress = (processed / total_fingerprints) * 100
                    print(f"Progress: {processed:,}/{total_fingerprints:,} ({progress:.1f}%) - Converted: {converted:,}")
            
            # Commit all changes
            conn.commit()
            
            # Vacuum the database to reclaim space
            print("Vacuuming database to reclaim space...")
            cursor.execute("VACUUM")
            
            print(f"Optimization complete! Converted {converted:,} fingerprints")
        
        # Get database size after optimization
        size_after = os.path.getsize(self.db_path)
        size_reduction = size_before - size_after
        reduction_percent = (size_reduction / size_before * 100) if size_before > 0 else 0
        
        return {
            'optimized': True,
            'total_fingerprints': total_fingerprints,
            'converted_fingerprints': converted,
            'size_before': size_before,
            'size_after': size_after,
            'size_reduction': size_reduction,
            'reduction_percent': reduction_percent
        }
    
    def get_database_size_info(self) -> Dict[str, any]:
        """
        Get detailed database size information.
        
        Returns:
            Dictionary with database size details.
        """
        import os
        
        size_bytes = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        size_mb = size_bytes / (1024 * 1024)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table sizes
            cursor.execute("SELECT COUNT(*) FROM Songs")
            song_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Fingerprints")
            fingerprint_count = cursor.fetchone()[0]
            
        return {
            'size_bytes': size_bytes,
            'size_mb': size_mb,
            'song_count': song_count,
            'fingerprint_count': fingerprint_count,
            'avg_bytes_per_fingerprint': size_bytes / fingerprint_count if fingerprint_count > 0 else 0
        }
