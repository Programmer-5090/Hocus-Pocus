"""
Debug script to test the identification process step by step.
"""

from ..src.core.engine import Engine
import os

def debug_identification():
    """Debug the identification process."""
    print("Debugging identification process...")
    
    # Initialize
    shazam = Engine()
    
    # Test with a known file first
    test_file = "Chill rap/Fake Love.mp3"
    
    if os.path.exists(test_file):
        print(f"\n1. Testing with known file: {test_file}")
        try:
            result = shazam.identify_song(test_file, max_duration=10.0)
            print("✅ Known file identification successful!")
            print(f"Match: {result.get('song_info', {}).get('title', 'Unknown')}")
        except Exception as e:
            print(f"❌ Error with known file: {e}")
            import traceback
            traceback.print_exc()
    
    # Test recording if that worked
    print(f"\n2. Testing audio recording...")
    try:
        # Just test the recording part
        recorded_file = shazam.audio_recorder.record()
        print(f"✅ Recording successful: {recorded_file}")
        
        # Test processing the recorded file
        print(f"\n3. Testing processing of recorded file...")
        analysis = shazam.process_audio_file(recorded_file)
        print(f"✅ Processing successful!")
        print(f"Duration: {analysis['duration']:.2f}s")
        print(f"Peaks: {len(analysis['peaks'])}")
        print(f"Fingerprints: {len(analysis['fingerprints'])}")
        
        # Test identification
        print(f"\n4. Testing identification of recorded file...")
        result = shazam.identify_song(recorded_file, max_duration=10.0)
        print("✅ Identification successful!")
        
    except Exception as e:
        print(f"❌ Error during recording/processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_identification()
