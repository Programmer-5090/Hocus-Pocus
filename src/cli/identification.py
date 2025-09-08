"""
Audio Identification Module

Handles real-time audio recording and song identification
for the Hocus Pocus terminal interface.

Author: Programmer-5090
Project: Hocus Pocus
"""

import time
from src.core.engine import Engine
from src.cli.interface import display_identification_results
from typing import Dict, Any


def perform_audio_identification(shazam_engine: Engine) -> bool:
    """
    Perform the complete audio identification process.
    
    Args:
        shazam_engine: Initialized Engine instance.
        
    Returns:
        True if identification was successful, False otherwise.
    """
    try:
        # Countdown for recording preparation
        print("\nStarting audio recording in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("RECORDING NOW! Play your song loud and clear...")
        
        # Record and process audio
        analysis_results = shazam_engine.process_audio_recording()
        
        # Display processing information
        duration = analysis_results.get('duration', 0)
        fingerprint_count = len(analysis_results.get('fingerprints', []))
        
        print(f"\nRecorded {duration:.1f} seconds of audio")
        print(f"Generated {fingerprint_count:,} fingerprints")
        print("Searching database for matches...")
        
        # Perform identification
        identification_result = shazam_engine.identify_song("output/recorded_audio.wav", max_duration=30.0)
        
        # Display results
        display_identification_results(identification_result)
        
        return identification_result.get('best_match_id') is not None
        
    except Exception as e:
        print(f"\nError during recording/identification: {e}")
        print("Please try again...")
        return False
