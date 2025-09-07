"""
Interactive Shazam Clone - Audio Identification System

This is the main entry point for the Shazam clone application, providing
an interactive command-line interface for real-time audio identification.

Features:
- Real-time microphone recording
- Advanced audio fingerprinting
- Database-driven song matching
- Professional user interface

Author: Shazam Clone Project
Version: 1.0
"""

from src.core.engine import Engine
import config
import os
import time
from typing import Dict, Any, List


def _check_and_optimize_database(shazam_engine: Engine) -> None:
    """
    Check if database optimization is needed and perform it automatically.
    
    This function ensures the database is always in an optimized state by
    checking for binary blob data and converting it to proper integers
    for better performance and storage efficiency.
    
    Args:
        shazam_engine: Initialized Engine instance.
    """
    print("🔍 Checking database optimization status...")
    
    db_manager = shazam_engine.db_manager
    
    # Check if optimization is needed
    if db_manager.needs_optimization():
        print("⚠️  Database optimization needed - found binary blob data")
        
        # Get current database size info
        size_info = db_manager.get_database_size_info()
        print(f"📊 Current database size: {size_info['size_mb']:.1f} MB ({size_info['fingerprint_count']:,} fingerprints)")
        
        # Ask user if they want to optimize now
        try:
            choice = input("\n🔧 Would you like to optimize the database now? This will improve performance and reduce size. (y/n): ").strip().lower()
            
            if choice in ['y', 'yes']:
                print("\n" + "=" * 60)
                print("🚀 STARTING AUTOMATIC DATABASE OPTIMIZATION")
                print("=" * 60)
                
                # Perform optimization
                optimization_result = db_manager.optimize_database()
                
                if optimization_result['optimized']:
                    print("\n" + "=" * 60)
                    print("✅ DATABASE OPTIMIZATION COMPLETE!")
                    print("=" * 60)
                    print(f"📊 Optimization Results:")
                    print(f"   • Converted fingerprints: {optimization_result['converted_fingerprints']:,}")
                    print(f"   • Size before: {optimization_result['size_before'] / (1024*1024):.1f} MB")
                    print(f"   • Size after: {optimization_result['size_after'] / (1024*1024):.1f} MB")
                    print(f"   • Space saved: {optimization_result['size_reduction'] / (1024*1024):.1f} MB")
                    print(f"   • Size reduction: {optimization_result['reduction_percent']:.1f}%")
                    print("⚡ Database is now optimized for better performance!")
                    print("=" * 60)
                else:
                    print(f"⚠️  Optimization not performed: {optimization_result.get('reason', 'Unknown reason')}")
            else:
                print("⏭️  Skipping database optimization. You can run it later if needed.")
                
        except (EOFError, KeyboardInterrupt):
            print("\n⏭️  Skipping database optimization.")
    else:
        print("✅ Database is already optimized!")


def interactive_identification_session():
    """
    Run the main interactive audio identification session.
    
    This function provides a user-friendly interface for real-time audio
    identification, allowing users to record audio from their microphone
    and receive instant song identification results.
    """
    print("🔍 Initializing Shazam Clone system...")
    
    # Initialize the audio identification engine
    shazam_engine = Engine()
    
    # Check and perform database optimization if needed
    _check_and_optimize_database(shazam_engine)
    
    # Verify database is ready
    database_stats = shazam_engine.get_database_stats()
    if database_stats['total_songs'] == 0:
        print("❌ No songs found in database. Please run bulk loading first.")
        return
    
    print("✅ Database ready with {} songs".format(database_stats['total_songs']))
    
    # Display welcome interface
    _display_welcome_message(database_stats)
    
    session_count = 0
    successful_identifications = 0
    
    try:
        while True:
            session_count += 1
            print(f"\n🎧 Session {session_count}")
            print("🎵 Play your song now and get ready...")
            
            # Get user input for identification
            user_choice = _get_user_choice()
            
            if user_choice == 'quit':
                break
            elif user_choice == 'yes':
                # Perform audio identification
                identification_result = _perform_audio_identification(shazam_engine)
                if identification_result:
                    successful_identifications += 1
            elif user_choice == 'upload':
                # Upload songs from a folder
                upload_result = _perform_folder_upload(shazam_engine)
                if upload_result:
                    # Update database stats after upload
                    database_stats = shazam_engine.get_database_stats()
                    print(f"✅ Database now contains {database_stats['total_songs']:,} songs and {database_stats['total_fingerprints']:,} fingerprints")
            else:
                print("⏭️  Skipping this session...")
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Identification session interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    # Display session summary
    _display_session_summary(session_count - 1, successful_identifications)


def _display_welcome_message(database_stats: Dict[str, Any]) -> None:
    """
    Display the welcome message and system status.
    
    Args:
        database_stats: Dictionary containing database statistics.
    """
    print("\n" + "=" * 60)
    print("🎵 INTERACTIVE SHAZAM CLONE - SONG IDENTIFICATION 🎵")
    print("=" * 60)
    print(f"✅ Database ready with {database_stats['total_songs']:,} songs and {database_stats['total_fingerprints']:,} fingerprints")
    
    print("\n📱 Instructions:")
    print("1. Play a song from your phone/speakers")
    print("2. When ready, I'll ask if you want to identify it")
    print("3. Type 'yes' to record and identify, 'no' to skip")
    print("4. Type 'upload' to add songs from a folder")
    print("5. Type 'quit' to exit the program")
    print("\n" + "=" * 60)


def _get_user_choice() -> str:
    """
    Get user input for identification choice.
    
    Returns:
        User's choice as a lowercase string ('yes', 'no', 'upload', or 'quit').
    """
    while True:
        try:
            choice = input("\n❓ Do you want to identify the audio? (yes/no/upload/quit): ").strip().lower()
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
                print("⚠️  Please enter 'yes', 'no', 'upload', or 'quit'")
        except (EOFError, KeyboardInterrupt):
            return 'quit'


def _perform_folder_upload(shazam_engine: Engine) -> bool:
    """
    Handle folder upload process with user-friendly interface.
    
    Args:
        shazam_engine: Initialized Engine instance.
        
    Returns:
        True if upload was successful, False otherwise.
    """
    try:
        print("\n" + "=" * 60)
        print("📁 FOLDER UPLOAD - ADD SONGS TO DATABASE")
        print("=" * 60)
        
        # Get folder path from user
        folder_path = _get_folder_path()
        if not folder_path:
            return False
        
        # Analyze folder structure
        folder_analysis = _analyze_folder_structure(folder_path)
        
        # Determine scanning method
        recursive = _choose_scanning_method(folder_path, folder_analysis)
        if recursive is None:  # User cancelled
            return False
        
        # Get supported audio files
        audio_files = _get_audio_files(folder_path, recursive)
        if not audio_files:
            print(f"❌ No supported audio files found in '{folder_path}'")
            if recursive:
                print("💡 No audio files found in this folder or any subdirectories")
            print(f"💡 Supported formats: {', '.join(sorted(config.SUPPORTED_AUDIO_FORMATS))}")
            return False
        
        total_files = len(audio_files)
        print(f"\n📁 Found {total_files} audio files to process...")
        
        # Confirm upload
        if not _confirm_upload(total_files, folder_path, recursive):
            return False
        
        # Perform bulk upload
        return _execute_bulk_upload(shazam_engine, audio_files, folder_path)
        
    except Exception as e:
        print(f"\n❌ Error during folder upload: {e}")
        return False


def _choose_scanning_method(folder_path: str, folder_analysis: Dict[str, Any]) -> bool:
    """
    Let user choose between recursive and non-recursive scanning based on folder analysis.
    
    Args:
        folder_path: Path to the folder being processed.
        folder_analysis: Analysis results from _analyze_folder_structure.
        
    Returns:
        True for recursive, False for non-recursive, None if cancelled.
    """
    print(f"\n📂 Folder Analysis: {os.path.basename(folder_path)}")
    print("=" * 50)
    
    # Display folder structure information
    if folder_analysis['has_subdirectories']:
        print(f"📁 Root directory: {folder_analysis['audio_files_in_root']} audio files")
        print(f"📁 Subdirectories: {folder_analysis['subdirectory_count']} found")
        print(f"📊 Total audio files (with subdirectories): ~{folder_analysis['estimated_total_audio_files']}")
        print(f"📊 Directory depth: {folder_analysis['max_depth']} levels deep")
        
        # Show some subdirectory names
        if folder_analysis['subdirectory_names']:
            print(f"\n📂 Sample subdirectories:")
            for i, subdir in enumerate(folder_analysis['subdirectory_names'][:5]):
                print(f"   • {subdir}")
            if len(folder_analysis['subdirectory_names']) > 5:
                print(f"   ... and {len(folder_analysis['subdirectory_names']) - 5} more")
        
        print(f"\n🔍 Scanning Options:")
        print(f"1. 📁 Current folder only ({folder_analysis['audio_files_in_root']} files)")
        print(f"2. 🌳 Recursive (all subdirectories, ~{folder_analysis['estimated_total_audio_files']} files)")
        print(f"3. ❌ Cancel upload")
        
        while True:
            try:
                choice = input(f"\n📂 Choose scanning method (1/2/3): ").strip()
                
                if choice == '1':
                    print("📁 Selected: Current folder only")
                    return False  # Non-recursive
                elif choice == '2':
                    print("🌳 Selected: Recursive scanning (includes all subdirectories)")
                    return True   # Recursive
                elif choice == '3':
                    print("❌ Upload cancelled")
                    return None   # Cancelled
                else:
                    print("⚠️  Please enter 1, 2, or 3")
                    
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Upload cancelled")
                return None
    else:
        # No subdirectories, just scan current folder
        print(f"📁 Single directory: {folder_analysis['audio_files_in_root']} audio files")
        print("📊 No subdirectories found - will scan current folder only")
        return False  # Non-recursive


def _get_folder_path() -> str:
    """
    Get and validate folder path from user input.
    
    Returns:
        Valid folder path or empty string if cancelled.
    """
    while True:
        try:
            print("\n📂 Enter the folder path containing your audio files:")
            print("💡 Examples:")
            print("   • C:\\Music\\MyPlaylist")
            print("   • ./music_folder")
            print("   • ../Songs")
            print("   • Type 'cancel' to go back")
            
            folder_path = input("\n📁 Folder path: ").strip()
            
            if folder_path.lower() in ['cancel', 'c', 'back', 'b']:
                print("⏭️  Upload cancelled.")
                return ""
            
            # Remove quotes if present
            folder_path = folder_path.strip('"\'')
            
            if not folder_path:
                print("⚠️  Please enter a folder path.")
                continue
            
            if not os.path.exists(folder_path):
                print(f"❌ Folder not found: '{folder_path}'")
                print("💡 Make sure the path is correct and the folder exists.")
                continue
            
            if not os.path.isdir(folder_path):
                print(f"❌ Path is not a folder: '{folder_path}'")
                continue
            
            return folder_path
            
        except (EOFError, KeyboardInterrupt):
            print("\n⏭️  Upload cancelled.")
            return ""


def _analyze_folder_structure(folder_path: str) -> Dict[str, Any]:
    """
    Analyze folder structure to help user decide between recursive and non-recursive scanning.
    
    Args:
        folder_path: Path to the folder to analyze.
        
    Returns:
        Dictionary with folder analysis results.
    """
    analysis = {
        'has_subdirectories': False,
        'subdirectory_count': 0,
        'subdirectory_names': [],
        'files_in_root': 0,
        'audio_files_in_root': 0,
        'estimated_total_audio_files': 0,
        'max_depth': 0
    }
    
    try:
        # Analyze root directory
        root_items = os.listdir(folder_path)
        subdirs = []
        
        for item in root_items:
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                analysis['files_in_root'] += 1
                _, ext = os.path.splitext(item.lower())
                if ext in config.SUPPORTED_AUDIO_FORMATS:
                    analysis['audio_files_in_root'] += 1
            elif os.path.isdir(item_path):
                subdirs.append(item)
        
        if subdirs:
            analysis['has_subdirectories'] = True
            analysis['subdirectory_count'] = len(subdirs)
            analysis['subdirectory_names'] = sorted(subdirs)
        
        # Quick recursive scan to estimate total files and depth
        if analysis['has_subdirectories']:
            total_audio_files = 0
            max_depth = 0
            
            for root, dirs, files in os.walk(folder_path):
                depth = root.replace(folder_path, '').count(os.sep)
                max_depth = max(max_depth, depth)
                
                for filename in files:
                    _, ext = os.path.splitext(filename.lower())
                    if ext in config.SUPPORTED_AUDIO_FORMATS:
                        total_audio_files += 1
            
            analysis['estimated_total_audio_files'] = total_audio_files
            analysis['max_depth'] = max_depth
        else:
            analysis['estimated_total_audio_files'] = analysis['audio_files_in_root']
    
    except Exception as e:
        print(f"❌ Error analyzing folder structure: {e}")
    
    return analysis


def _get_audio_files(folder_path: str, recursive: bool = False) -> List[str]:
    """
    Get all supported audio files from the specified folder.
    
    Args:
        folder_path: Path to the folder to scan.
        recursive: If True, scan subdirectories recursively.
        
    Returns:
        List of audio file paths.
    """
    audio_files = []
    
    try:
        if recursive:
            # Recursive scanning using os.walk
            print(f"🔍 Scanning '{folder_path}' recursively...")
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    _, ext = os.path.splitext(filename.lower())
                    if ext in config.SUPPORTED_AUDIO_FORMATS:
                        audio_files.append(file_path)
                        
                # Show progress for large directory structures
                if len(audio_files) % 100 == 0 and len(audio_files) > 0:
                    relative_path = os.path.relpath(root, folder_path)
                    if relative_path != '.':
                        print(f"   📂 Scanning: {relative_path}/ ({len(audio_files)} files found so far)")
        else:
            # Non-recursive scanning (current directory only)
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename.lower())
                    if ext in config.SUPPORTED_AUDIO_FORMATS:
                        audio_files.append(file_path)
        
        # Sort files for consistent processing order
        audio_files.sort()
        return audio_files
        
    except Exception as e:
        print(f"❌ Error scanning folder: {e}")
        return []


def _confirm_upload(total_files: int, folder_path: str, recursive: bool = False) -> bool:
    """
    Get user confirmation for the upload process.
    
    Args:
        total_files: Number of files to upload.
        folder_path: Path to the source folder.
        recursive: Whether recursive scanning was used.
        
    Returns:
        True if user confirms, False otherwise.
    """
    print(f"\n📊 Upload Summary:")
    print(f"   • Folder: {folder_path}")
    print(f"   • Scan method: {'🌳 Recursive (includes subdirectories)' if recursive else '📁 Current folder only'}")
    print(f"   • Files to process: {total_files}")
    print(f"   • Estimated time: {total_files * 2:.0f}-{total_files * 5:.0f} seconds")
    print(f"\n⚠️  This will:")
    print(f"   • Process {total_files} audio files")
    print(f"   • Generate audio fingerprints for each song")
    print(f"   • Add songs to your database")
    print(f"   • Automatically optimize the database afterward")
    
    while True:
        try:
            choice = input(f"\n🚀 Continue with upload? (yes/no): ").strip().lower()
            if choice in ['yes', 'y']:
                return True
            elif choice in ['no', 'n']:
                print("⏭️  Upload cancelled.")
                return False
            else:
                print("⚠️  Please enter 'yes' or 'no'")
        except (EOFError, KeyboardInterrupt):
            print("\n⏭️  Upload cancelled.")
            return False


def _execute_bulk_upload(shazam_engine: Engine, audio_files: List[str], folder_path: str) -> bool:
    """
    Execute the bulk upload process.
    
    Args:
        shazam_engine: Initialized Engine instance.
        audio_files: List of audio file paths to process.
        folder_path: Source folder path for display.
        
    Returns:
        True if upload was successful, False otherwise.
    """
    print(f"\n⚡ Starting bulk upload from '{folder_path}'...")
    print("📊 Processing files (this may take a while)...\n")
    

    total_files = len(audio_files)
    successful_imports = 0
    failed_imports = 0
    
    for i, file_path in enumerate(audio_files, 1):
        # Get relative path for better display in nested structures
        relative_path = os.path.relpath(file_path, folder_path)
        filename = os.path.basename(file_path)
        
        # Extract title from filename (remove extension)
        title = os.path.splitext(filename)[0]
        
        # Enhanced artist/title extraction for nested folders
        artist = "Unknown Artist"
        
        # Try to extract artist from folder structure
        path_parts = relative_path.split(os.sep)
        if len(path_parts) > 1:
            # Use parent folder as potential artist/genre info
            parent_folder = path_parts[-2]
            if not parent_folder.lower() in ['music', 'songs', 'tracks', 'audio']:
                artist = parent_folder
        
        # Override with filename-based artist extraction if available
        if " - " in title:
            parts = title.split(" - ", 1)
            if len(parts) == 2:
                artist, title = parts[0].strip(), parts[1].strip()
        elif " feat. " in title:
            title = title.split(" feat. ")[0].strip()
        elif " (feat. " in title:
            title = title.split(" (feat. ")[0].strip()
        
        # Display progress with relative path for nested structures
        if len(path_parts) > 1:
            display_path = "/".join(path_parts[:-1]) + "/"
            print(f"[{i:2d}/{total_files}] 📂 {display_path}{title}")
        else:
            print(f"[{i:2d}/{total_files}] Processing: {title}")
        
        try:
            # Add song to database (processes audio and creates fingerprints)
            song_id = shazam_engine.add_song_to_database(
                file_path=file_path,
                title=title,
                artist=artist
            )
            
            print(f"    ✅ Successfully added (Song ID: {song_id})")
            successful_imports += 1
            
        except Exception as e:
            print(f"    ❌ Failed: {str(e)}")
            failed_imports += 1
        
        # Show progress every 10 songs
        if i % 10 == 0:
            print(f"\n--- Progress: {i}/{total_files} files processed ---")
            print(f"    ✅ Successful: {successful_imports}")
            print(f"    ❌ Failed: {failed_imports}\n")
    
    # Display upload summary
    _display_upload_summary(total_files, successful_imports, failed_imports, folder_path, shazam_engine)
    
    # Automatically optimize database after upload
    if successful_imports > 0:
        print("\n🔧 Performing automatic database optimization after upload...")
        _check_and_optimize_database(shazam_engine)
    
    return successful_imports > 0


def _display_upload_summary(total_files: int, successful_imports: int, failed_imports: int, 
                           folder_path: str, shazam_engine: Engine) -> None:
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
    print("📁 FOLDER UPLOAD SUMMARY")
    print("=" * 60)
    print(f"📂 Source folder: {folder_path}")
    print(f"📁 Total files processed: {total_files}")
    print(f"✅ Successfully imported: {successful_imports}")
    print(f"❌ Failed imports: {failed_imports}")
    
    if total_files > 0:
        success_rate = (successful_imports / total_files) * 100
        print(f"📈 Success rate: {success_rate:.1f}%")
    
    # Show final database stats
    stats = shazam_engine.get_database_stats()
    print(f"\n📊 Updated database statistics:")
    print(f"🎵 Total songs in database: {stats['total_songs']:,}")
    print(f"🔑 Total fingerprints: {stats['total_fingerprints']:,}")
    print("=" * 60)


def _perform_audio_identification(shazam_engine: Engine) -> bool:
    """
    Perform the complete audio identification process.
    
    Args:
        shazam_engine: Initialized Engine instance.
        
    Returns:
        True if identification was successful, False otherwise.
    """
    try:
        # Countdown for recording preparation
        print("\n🎤 Starting audio recording in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("🔴 RECORDING NOW! Play your song loud and clear...")
        
        # Record and process audio
        analysis_results = shazam_engine.process_audio_recording()
        
        # Display processing information
        duration = analysis_results.get('duration', 0)
        fingerprint_count = len(analysis_results.get('fingerprints', []))
        
        print(f"\n📊 Recorded {duration:.1f} seconds of audio")
        print(f"🔍 Generated {fingerprint_count:,} fingerprints")
        print("🔎 Searching database for matches...")
        
        # Perform identification
        identification_result = shazam_engine.identify_song("output/recorded_audio.wav", max_duration=30.0)
        
        # Display results
        _display_identification_results(identification_result)
        
        return identification_result.get('best_match_id') is not None
        
    except Exception as e:
        print(f"\n❌ Error during recording/identification: {e}")
        print("Please try again...")
        return False


def _display_identification_results(result: Dict[str, Any]) -> None:
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
        print("🎯 IDENTIFICATION RESULTS")
        print("=" * 50)
        print("🎵 MATCH FOUND!")
        print(f"📀 Song: {song_info.get('title', 'Unknown')}")
        print(f"🎤 Artist: {song_info.get('artist', 'Unknown Artist')}")
        print(f"⭐ Confidence: {confidence:.1f}%")
        print(f"🎯 Match Score: {score}")
        print(f"⏱️  Time Offset: {offset} frames")
        print(f"💿 Song ID: {song_info.get('song_id', 'Unknown')}")
        print(f"⏳ Full Song Duration: {song_duration:.1f} seconds")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ NO MATCH FOUND")
        print("=" * 50)
        print("🔍 No matching song found in the database.")
        print("💡 Try:")
        print("   • Playing the song louder")
        print("   • Reducing background noise")
        print("   • Playing a different part of the song")
        print("   • Ensuring the song is in the database")
        print("=" * 50)


def _display_session_summary(total_sessions: int, successful_identifications: int) -> None:
    """
    Display the final session summary.
    
    Args:
        total_sessions: Total number of identification attempts.
        successful_identifications: Number of successful identifications.
    """
    print("\n👋 Goodbye! Thanks for using Shazam Clone!")
    print(f"\n📊 Session completed! Total identification attempts: {total_sessions}")
    
    if total_sessions > 0:
        success_rate = (successful_identifications / total_sessions) * 100
        print(f"✅ Successful identifications: {successful_identifications}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        

def _display_bulk_import_summary(total_files: int, successful_imports: int, 
                                failed_imports: int, shazam_engine: Engine) -> None:
    """
    Display the bulk import summary.
    
    Args:
        total_files: Total number of files processed.
        successful_imports: Number of successful imports.
        failed_imports: Number of failed imports.
        shazam_engine: Engine instance for getting final stats.
    """
    print("\n" + "=" * 60)
    print("BULK IMPORT SUMMARY")
    print("=" * 60)
    print(f"📁 Total files processed: {total_files}")
    print(f"✅ Successfully imported: {successful_imports}")
    print(f"❌ Failed imports: {failed_imports}")
    print(f"📈 Success rate: {(successful_imports/total_files)*100:.1f}%")
    
    # Show final database stats
    stats = shazam_engine.get_database_stats()
    print(f"\n📊 Final database statistics:")
    print(f"🎵 Total songs in database: {stats['total_songs']:,}")
    print(f"🔑 Total fingerprints: {stats['total_fingerprints']:,}")
    print("=" * 60)


if __name__ == "__main__":
    """
    Main entry point for the Shazam Clone application.
    
    Ensures required directories exist and launches the interactive
    identification session.
    """
    # Ensure all required directories exist
    config.ensure_directories()
    
    # Launch the interactive identification session
    interactive_identification_session()
    
    # Uncomment the line below to run bulk loading instead:
    # bulk_load_chill_rap_songs()
