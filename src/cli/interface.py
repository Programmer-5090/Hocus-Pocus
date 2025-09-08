"""
User Interface and Display Module

Handles user interaction, input validation, and display formatting
for the Hocus Pocus terminal interface.

Author: Programmer-5090
Project: Hocus Pocus
"""

from typing import Dict, Any


def display_welcome_message(database_stats: Dict[str, Any]) -> None:
    """
    Display the welcome message and system status.
    
    Args:
        database_stats: Dictionary containing database statistics.
    """
    print("\n" + "=" * 60)
    print("INTERACTIVE HOCUS POCUS - SONG IDENTIFICATION")
    print("=" * 60)
    print(f"Database ready with {database_stats['total_songs']:,} songs and {database_stats['total_fingerprints']:,} fingerprints")
    
    print("\nInstructions:")
    print("1. Play a song from your phone/speakers")
    print("2. When ready, I'll ask if you want to identify it")
    print("3. Type 'yes' to record and identify, 'no' to skip")
    print("4. Type 'upload' to add songs from a folder")
    print("5. Type 'quit' to exit the program")
    print("\n" + "=" * 60)


def get_user_choice() -> str:
    """
    Get user input for identification choice.
    
    Returns:
        User's choice as a lowercase string ('yes', 'no', 'upload', or 'quit').
    """
    while True:
        try:
            choice = input("\nDo you want to identify the audio? (yes/no/upload/quit): ").strip().lower()
            if choice in ['yes', 'y', 'no', 'n', 'upload', 'u', 'quit', 'q', 'exit']:
                if choice in ['y', 'yes']:
                    return 'yes'
                elif choice in ['n', 'no']:
                    return 'no'
                elif choice in ['u', 'upload']:
                    return 'upload'
                elif choice in ['q', 'quit', 'exit']:
                    return 'quit'
            else:
                print("Please enter 'yes', 'no', 'upload', or 'quit'")
        except (EOFError, KeyboardInterrupt):
            return 'quit'


def display_identification_results(result: Dict[str, Any]) -> None:
    """
    Display formatted identification results.
    
    Args:
        result: Dictionary containing identification results.
    """
    if result.get('best_match_id'):
        song_info = result.get('song_info', {})
        confidence = result.get('confidence', 0) * 100
        score = result.get('best_score', 0)
        offset = result.get('best_offset', 0)
        song_duration = song_info.get('duration', 0)
        
        print("\n" + "=" * 50)
        print("IDENTIFICATION RESULTS")
        print("=" * 50)
        print("MATCH FOUND!")
        print(f"Song: {song_info.get('title', 'Unknown')}")
        print(f"Artist: {song_info.get('artist', 'Unknown Artist')}")
        print(f"Confidence: {confidence:.1f}%")
        print(f"Match Score: {score}")
        print(f"Time Offset: {offset} frames")
        print(f"Song ID: {song_info.get('song_id', 'Unknown')}")
        print(f"Full Song Duration: {song_duration:.1f} seconds")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("NO MATCH FOUND")
        print("=" * 50)
        print("No matching song found in the database.")
        print("Try:")
        print("   • Playing the song louder")
        print("   • Reducing background noise")
        print("   • Playing a different part of the song")
        print("   • Ensuring the song is in the database")
        print("=" * 50)


def display_session_summary(total_sessions: int, successful_identifications: int) -> None:
    """
    Display the final session summary.
    
    Args:
        total_sessions: Total number of identification attempts.
        successful_identifications: Number of successful identifications.
    """
    print("\nGoodbye! Thanks for using Hocus Pocus!")
    print(f"\nSession completed! Total identification attempts: {total_sessions}")
    
    if total_sessions > 0:
        success_rate = (successful_identifications / total_sessions) * 100
        print(f"Successful identifications: {successful_identifications}")
        print(f"Success rate: {success_rate:.1f}%")


def display_upload_summary(total_files: int, successful_imports: int, failed_imports: int, 
                          folder_path: str, shazam_engine) -> None:
    """
    Display the upload summary with statistics.
    
    Args:
        total_files: Total number of files processed.
        successful_imports: Number of successful imports.
        failed_imports: Number of failed imports.
        folder_path: Source folder path.
        shazam_engine: Engine instance for getting final stats.
    """
    print("\n" + "=" * 60)
    print("FOLDER UPLOAD SUMMARY")
    print("=" * 60)
    print(f"Source folder: {folder_path}")
    print(f"Total files processed: {total_files}")
    print(f"Successfully imported: {successful_imports}")
    print(f"Failed imports: {failed_imports}")
    
    if total_files > 0:
        success_rate = (successful_imports / total_files) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    # Show final database stats
    stats = shazam_engine.get_database_stats()
    print(f"\nUpdated database statistics:")
    print(f"Total songs in database: {stats['total_songs']:,}")
    print(f"Total fingerprints: {stats['total_fingerprints']:,}")
    print("=" * 60)
