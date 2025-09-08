"""
Folder Upload Module

Handles batch upload of audio files from folders
for the Hocus Pocus terminal interface.

Author: Programmer-5090
Project: Hocus Pocus
"""

import os
import config
from src.core.engine import Engine
from src.cli.interface import display_upload_summary
from src.cli.database_optimizer import check_and_optimize_database
from typing import Dict, Any, List


def perform_folder_upload(shazam_engine: Engine) -> bool:
    """
    Handle folder upload process with user-friendly interface.
    
    Args:
        shazam_engine: Initialized Engine instance.
        
    Returns:
        True if upload was successful, False otherwise.
    """
    try:
        print("\n" + "=" * 60)
        print("FOLDER UPLOAD - ADD SONGS TO DATABASE")
        print("=" * 60)
        
        # Get folder path from user
        folder_path = get_folder_path()
        if not folder_path:
            return False
        
        # Analyze folder structure
        folder_analysis = analyze_folder_structure(folder_path)
        
        # Determine scanning method
        recursive = choose_scanning_method(folder_path, folder_analysis)
        if recursive is None:  # User cancelled
            return False
        
        # Get supported audio files
        audio_files = get_audio_files(folder_path, recursive)
        if not audio_files:
            print(f"No supported audio files found in '{folder_path}'")
            if recursive:
                print("No audio files found in this folder or any subdirectories")
            print(f"Supported formats: {', '.join(sorted(config.SUPPORTED_AUDIO_FORMATS))}")
            return False
        
        total_files = len(audio_files)
        print(f"\nFound {total_files} audio files to process...")
        
        # Confirm upload
        if not confirm_upload(total_files, folder_path, recursive):
            return False
        
        # Perform bulk upload
        return execute_bulk_upload(shazam_engine, audio_files, folder_path)
        
    except Exception as e:
        print(f"\nError during folder upload: {e}")
        return False


def get_folder_path() -> str:
    """
    Get and validate folder path from user input.
    
    Returns:
        Valid folder path or empty string if cancelled.
    """
    while True:
        try:
            print("\nEnter the folder path containing your audio files:")
            print("Examples:")
            print("   • C:\\Music\\MyPlaylist")
            print("   • ./music_folder")
            print("   • ../Songs")
            print("   • Type 'cancel' to go back")
            
            folder_path = input("\nFolder path: ").strip()
            
            if folder_path.lower() in ['cancel', 'c', 'back', 'b']:
                print("Upload cancelled.")
                return ""
            
            # Remove quotes if present
            folder_path = folder_path.strip('"\'')
            
            if not folder_path:
                print("Please enter a folder path.")
                continue
            
            if not os.path.exists(folder_path):
                print(f"Folder not found: '{folder_path}'")
                print("Make sure the path is correct and the folder exists.")
                continue
            
            if not os.path.isdir(folder_path):
                print(f"Path is not a folder: '{folder_path}'")
                continue
            
            return folder_path
            
        except (EOFError, KeyboardInterrupt):
            print("\nUpload cancelled.")
            return ""


def analyze_folder_structure(folder_path: str) -> Dict[str, Any]:
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
        print(f"Error analyzing folder structure: {e}")
    
    return analysis


def choose_scanning_method(folder_path: str, folder_analysis: Dict[str, Any]) -> bool:
    """
    Let user choose between recursive and non-recursive scanning based on folder analysis.
    
    Args:
        folder_path: Path to the folder being processed.
        folder_analysis: Analysis results from analyze_folder_structure.
        
    Returns:
        True for recursive, False for non-recursive, None if cancelled.
    """
    print(f"\nFolder Analysis: {os.path.basename(folder_path)}")
    print("=" * 50)
    
    # Display folder structure information
    if folder_analysis['has_subdirectories']:
        print(f"Root directory: {folder_analysis['audio_files_in_root']} audio files")
        print(f"Subdirectories: {folder_analysis['subdirectory_count']} found")
        print(f"Total audio files (with subdirectories): ~{folder_analysis['estimated_total_audio_files']}")
        print(f"Directory depth: {folder_analysis['max_depth']} levels deep")
        
        # Show some subdirectory names
        if folder_analysis['subdirectory_names']:
            print(f"\nSample subdirectories:")
            for i, subdir in enumerate(folder_analysis['subdirectory_names'][:5]):
                print(f"   • {subdir}")
            if len(folder_analysis['subdirectory_names']) > 5:
                print(f"   ... and {len(folder_analysis['subdirectory_names']) - 5} more")
        
        print(f"\nScanning Options:")
        print(f"1. Current folder only ({folder_analysis['audio_files_in_root']} files)")
        print(f"2. Recursive (all subdirectories, ~{folder_analysis['estimated_total_audio_files']} files)")
        print(f"3. Cancel upload")
        
        while True:
            try:
                choice = input(f"\nChoose scanning method (1/2/3): ").strip()
                
                if choice == '1':
                    print("Selected: Current folder only")
                    return False  # Non-recursive
                elif choice == '2':
                    print("Selected: Recursive scanning (includes all subdirectories)")
                    return True   # Recursive
                elif choice == '3':
                    print("Upload cancelled")
                    return None   # Cancelled
                else:
                    print("Please enter 1, 2, or 3")
                    
            except (EOFError, KeyboardInterrupt):
                print("\nUpload cancelled")
                return None
    else:
        # No subdirectories, just scan current folder
        print(f"Single directory: {folder_analysis['audio_files_in_root']} audio files")
        print("No subdirectories found - will scan current folder only")
        return False  # Non-recursive


def get_audio_files(folder_path: str, recursive: bool = False) -> List[str]:
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
            print(f"Scanning '{folder_path}' recursively...")
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
                        print(f"   Scanning: {relative_path}/ ({len(audio_files)} files found so far)")
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
        print(f"Error scanning folder: {e}")
        return []


def confirm_upload(total_files: int, folder_path: str, recursive: bool = False) -> bool:
    """
    Get user confirmation for the upload process.
    
    Args:
        total_files: Number of files to upload.
        folder_path: Path to the source folder.
        recursive: Whether recursive scanning was used.
        
    Returns:
        True if user confirms, False otherwise.
    """
    print(f"\nUpload Summary:")
    print(f"   • Folder: {folder_path}")
    print(f"   • Scan method: {'Recursive (includes subdirectories)' if recursive else 'Current folder only'}")
    print(f"   • Files to process: {total_files}")
    print(f"   • Estimated time: {total_files * 2:.0f}-{total_files * 5:.0f} seconds")
    print(f"\nThis will:")
    print(f"   • Process {total_files} audio files")
    print(f"   • Generate audio fingerprints for each song")
    print(f"   • Add songs to your database")
    print(f"   • Automatically optimize the database afterward")
    
    while True:
        try:
            choice = input(f"\nContinue with upload? (yes/no): ").strip().lower()
            if choice in ['yes', 'y']:
                return True
            elif choice in ['no', 'n']:
                print("Upload cancelled.")
                return False
            else:
                print("Please enter 'yes' or 'no'")
        except (EOFError, KeyboardInterrupt):
            print("\nUpload cancelled.")
            return False


def execute_bulk_upload(shazam_engine: Engine, audio_files: List[str], folder_path: str) -> bool:
    """
    Execute the bulk upload process.
    
    Args:
        shazam_engine: Initialized Engine instance.
        audio_files: List of audio file paths to process.
        folder_path: Source folder path for display.
        
    Returns:
        True if upload was successful, False otherwise.
    """
    print(f"\nStarting bulk upload from '{folder_path}'...")
    print("Processing files (this may take a while)...\n")
    
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
            print(f"[{i:2d}/{total_files}] {display_path}{title}")
        else:
            print(f"[{i:2d}/{total_files}] Processing: {title}")
        
        try:
            # Add song to database (processes audio and creates fingerprints)
            song_id = shazam_engine.add_song_to_database(
                file_path=file_path,
                title=title,
                artist=artist
            )
            
            print(f"    Successfully added (Song ID: {song_id})")
            successful_imports += 1
            
        except Exception as e:
            print(f"    Failed: {str(e)}")
            failed_imports += 1
        
        # Show progress every 10 songs
        if i % 10 == 0:
            print(f"\n--- Progress: {i}/{total_files} files processed ---")
            print(f"    Successful: {successful_imports}")
            print(f"    Failed: {failed_imports}\n")
    
    # Display upload summary
    display_upload_summary(total_files, successful_imports, failed_imports, folder_path, shazam_engine)
    
    # Automatically optimize database after upload
    if successful_imports > 0:
        print("\nPerforming automatic database optimization after upload...")
        check_and_optimize_database(shazam_engine)
    
    return successful_imports > 0
