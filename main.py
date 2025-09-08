"""
Hocus Pocus - Terminal-Based Audio Identification System

Main entry point for the Hocus Pocus application, providing
an interactive command-line interface for real-time audio identification.

Features:
- Real-time microphone recording
- Advanced audio fingerprinting
- Database-driven song matching
- Professional terminal interface

Author: Programmer-5090
Project: Hocus Pocus
Version: 1.0
"""

from src.core.engine import Engine
from src.cli.database_optimizer import check_and_optimize_database
from src.cli.interface import (
    display_welcome_message, 
    get_user_choice, 
    display_session_summary
)
from src.cli.identification import perform_audio_identification
from src.cli.folder_upload import perform_folder_upload
import config


def main():
    """
    Main entry point for the Hocus Pocus application.
    
    Ensures required directories exist and launches the interactive
    identification session.
    """
    # Ensure all required directories exist
    config.ensure_directories()
    
    # Launch the interactive identification session
    interactive_identification_session()


def interactive_identification_session():
    """
    Run the main interactive audio identification session.
    
    This function provides a user-friendly interface for real-time audio
    identification, allowing users to record audio from their microphone
    and receive instant song identification results.
    """
    print("Initializing Hocus Pocus system...")
    
    # Initialize the audio identification engine
    shazam_engine = Engine()
    
    # Check and perform database optimization if needed
    check_and_optimize_database(shazam_engine)
    
    # Verify database is ready
    database_stats = shazam_engine.get_database_stats()
    if database_stats['total_songs'] == 0:
        print("No songs found in database. Please run bulk loading first.")
        return
    
    print("Database ready with {} songs".format(database_stats['total_songs']))
    
    # Display welcome interface
    display_welcome_message(database_stats)
    
    session_count = 0
    successful_identifications = 0
    
    try:
        while True:
            session_count += 1
            print(f"\nSession {session_count}")
            print("Play your song now and get ready...")
            
            # Get user input for identification
            user_choice = get_user_choice()
            
            if user_choice == 'quit':
                break
            elif user_choice == 'yes':
                # Perform audio identification
                identification_result = perform_audio_identification(shazam_engine)
                if identification_result:
                    successful_identifications += 1
            elif user_choice == 'upload':
                # Upload songs from a folder
                upload_result = perform_folder_upload(shazam_engine)
                if upload_result:
                    # Update database stats after upload
                    database_stats = shazam_engine.get_database_stats()
                    print(f"Database now contains {database_stats['total_songs']:,} songs and {database_stats['total_fingerprints']:,} fingerprints")
            else:
                print("Skipping this session...")
                
    except KeyboardInterrupt:
        print("\n\nIdentification session interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    # Display session summary
    display_session_summary(session_count - 1, successful_identifications)


if __name__ == "__main__":
    main()
