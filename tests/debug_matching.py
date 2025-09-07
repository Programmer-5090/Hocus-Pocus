#!/usr/bin/env python3
"""
Fingerprint Matching Debug Script

This script helps debug why songs aren't matching after database optimization
by analyzing the fingerprint generation and matching process step by step.
"""

import sqlite3
from ..src.core.engine import Engine
import struct

def debug_fingerprint_matching():
    """Debug the fingerprint matching process."""
    
    print("🔍 DEBUGGING FINGERPRINT MATCHING PROCESS")
    print("=" * 60)
    
    # Initialize Shazam engine
    shazam = Engine()
    
    # Step 1: Test with a known song from the database
    print("\n📋 Step 1: Get a sample song from database")
    conn = sqlite3.connect("shazam_clone.db")
    cursor = conn.cursor()
    
    # Get first song info
    cursor.execute("SELECT song_id, title, file_path FROM Songs LIMIT 1")
    song_info = cursor.fetchone()
    song_id, title, file_path = song_info
    print(f"   🎵 Testing with: {title} (ID: {song_id})")
    print(f"   📁 File: {file_path}")
    
    # Step 2: Get some fingerprints from database for this song
    print(f"\n📋 Step 2: Sample fingerprints from database for song {song_id}")
    cursor.execute("""
        SELECT f_anchor, f_target, delta_t, t_anchor 
        FROM Fingerprints 
        WHERE song_id = ? 
        LIMIT 5
    """, (song_id,))
    
    db_fingerprints = cursor.fetchall()
    print(f"   📊 Found {len(db_fingerprints)} sample fingerprints:")
    for i, (f_anchor, f_target, delta_t, t_anchor) in enumerate(db_fingerprints):
        print(f"      {i+1}: f_anchor={f_anchor} ({type(f_anchor)}), f_target={f_target} ({type(f_target)})")
        print(f"         delta_t={delta_t} ({type(delta_t)}), t_anchor={t_anchor} ({type(t_anchor)})")
    
    conn.close()
    
    # Step 3: Process the same song file to generate fingerprints
    print(f"\n📋 Step 3: Generate fingerprints from the same audio file")
    try:
        analysis_results = shazam.process_audio_file(file_path)
        generated_fingerprints = analysis_results['fingerprints']
        print(f"   📊 Generated {len(generated_fingerprints)} fingerprints")
        
        # Show sample generated fingerprints
        print(f"   📄 Sample generated fingerprints:")
        for i, fp in enumerate(generated_fingerprints[:5]):
            hash_fp, t_anchor = fp
            f_anchor, f_target, delta_t = hash_fp
            print(f"      {i+1}: f_anchor={f_anchor} ({type(f_anchor)}), f_target={f_target} ({type(f_target)})")
            print(f"         delta_t={delta_t} ({type(delta_t)}), t_anchor={t_anchor} ({type(t_anchor)})")
            
    except Exception as e:
        print(f"   ❌ Error processing audio file: {e}")
        return
    
    # Step 4: Test direct matching
    print(f"\n📋 Step 4: Test direct fingerprint matching")
    
    # Take first few generated fingerprints and try to match them
    test_fingerprints = generated_fingerprints[:10]
    print(f"   🔍 Testing with {len(test_fingerprints)} fingerprints...")
    
    conn = sqlite3.connect("shazam_clone.db")
    cursor = conn.cursor()
    
    matches_found = 0
    for i, (hash_fp, t_anchor_query) in enumerate(test_fingerprints):
        f_anchor, f_target, delta_t = hash_fp
        
        cursor.execute('''
            SELECT song_id, t_anchor 
            FROM Fingerprints
            WHERE f_anchor=? AND f_target=? AND delta_t=?
        ''', (f_anchor, f_target, delta_t))
        
        matches = cursor.fetchall()
        if matches:
            matches_found += 1
            print(f"      ✅ Fingerprint {i+1}: Found {len(matches)} matches")
            for song_match_id, t_anchor_db in matches[:3]:  # Show first 3 matches
                print(f"         Song {song_match_id}: t_anchor_db={t_anchor_db}, t_anchor_query={t_anchor_query}")
        else:
            print(f"      ❌ Fingerprint {i+1}: No matches found")
            print(f"         Looking for: f_anchor={f_anchor}, f_target={f_target}, delta_t={delta_t}")
    
    conn.close()
    
    print(f"\n   📊 Direct matching results: {matches_found}/{len(test_fingerprints)} fingerprints found matches")
    
    # Step 5: Test full identification
    print(f"\n📋 Step 5: Test full song identification")
    try:
        # Test identification with the same file
        result = shazam.identify_song(file_path, max_duration=15.0)
        
        print(f"   📊 Identification result:")
        print(f"      Best match ID: {result.get('best_match_id')}")
        print(f"      Scores count: {len(result.get('scores', {}))}")
        
        if result.get('best_match_id'):
            print(f"      ✅ SUCCESS: Song was identified!")
            print(f"      Match details: {result.get('song_info', {})}")
        else:
            print(f"      ❌ FAILED: Song was not identified")
            
            # Show top scores if any
            scores = result.get('scores', {})
            if scores:
                sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                print(f"      Top scores:")
                for (song_id, offset), score in sorted_scores[:5]:
                    print(f"         Song {song_id} (offset {offset}): {score} matches")
        
    except Exception as e:
        print(f"   ❌ Error during identification: {e}")
    
    # Step 6: Check database statistics
    print(f"\n📋 Step 6: Database statistics")
    conn = sqlite3.connect("shazam_clone.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Fingerprints")
    total_fingerprints = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT song_id) FROM Fingerprints")
    songs_with_fingerprints = cursor.fetchone()[0]
    
    cursor.execute("SELECT song_id, COUNT(*) FROM Fingerprints GROUP BY song_id ORDER BY COUNT(*) DESC LIMIT 5")
    top_songs = cursor.fetchall()
    
    print(f"   📊 Total fingerprints: {total_fingerprints:,}")
    print(f"   📊 Songs with fingerprints: {songs_with_fingerprints}")
    print(f"   📊 Top songs by fingerprint count:")
    for song_id, count in top_songs:
        print(f"      Song {song_id}: {count:,} fingerprints")
    
    conn.close()

if __name__ == "__main__":
    debug_fingerprint_matching()
