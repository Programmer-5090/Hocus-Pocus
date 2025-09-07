"""
Shazam Clone Engine - Audio Fingerprinting and Identification System

This module provides the main orchestration class for the Shazam clone system,
integrating all components including audio loading, processing, fingerprinting,
and database management for real-time audio identification.

Key Components:
- Audio loading and recording from multiple sources
- Advanced spectrogram processing and peak detection
- Constellation mapping for audio fingerprinting
- Database storage and retrieval of audio fingerprints
- Real-time audio identification and matching

Author: Hocus Pocus Project
Version: 1.0
"""

from typing import Dict, List, Tuple, Optional, Any
from ..audio.audio_loader import AudioLoader
from ..audio.spectrogram_processor import SpectrogramProcessor
from ..audio.audio_visualizer import AudioVisualizer
from ..audio.audio_recorder import AudioRecorder
from .fingerprint_generator import FingerprintGenerator
from ..database.database_manager import DatabaseManager


class Engine:
    """
    Main orchestration class for the audio fingerprinting system.
    
    This class integrates all components of the Shazam clone system to provide
    complete audio identification functionality, from recording and processing
    to database storage and song matching.
    """
    
    def __init__(self, fft_size: int = 2048, hop_length: int = 512, 
                 fan_value: int = 5, target_zone: Tuple[int, int] = (1, 20),
                 db_path: str = None):
        """
        Initialize the comprehensive audio identification system.
        
        Args:
            fft_size: Size of the FFT window for spectrogram analysis (default: 2048)
            hop_length: Number of samples between successive frames (default: 512)
            fan_value: Number of target peaks to pair with each anchor peak (default: 5)
            target_zone: Time difference range for valid fingerprint pairs (default: (1, 20))
            db_path: Path to the SQLite database file (default: uses config.DATABASE_PATH)
        """
        # Use config database path if none provided
        if db_path is None:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            import config
            db_path = config.DATABASE_PATH
        
        # Initialize core audio processing components
        self.audio_loader = AudioLoader()
        self.audio_recorder = AudioRecorder(config.RECORDED_AUDIO_PATH, duration=15)
        self.spectrogram_processor = SpectrogramProcessor(fft_size, hop_length)
        self.visualizer = AudioVisualizer()
        self.fingerprint_generator = FingerprintGenerator(fan_value, target_zone)
        self.db_manager = DatabaseManager(db_path)
    
    def process_audio_file(self, file_path: str, sample_rate: int = 22050) -> Dict[str, Any]:
        """
        Process an audio file and return comprehensive analysis results.
        
        This method performs complete audio analysis including loading, spectrogram
        computation, peak detection, and fingerprint generation for a given audio file.
        
        Args:
            file_path: Path to the audio file to process
            sample_rate: Target sample rate for processing (default: 22050 Hz)
            
        Returns:
            Dictionary containing comprehensive analysis results with keys:
            - 'file_path': Original file path
            - 'signal': Normalized audio signal array
            - 'sample_rate': Actual sample rate used
            - 'duration': Audio duration in seconds
            - 'spectrogram': Computed spectrogram matrix
            - 'peaks': Detected constellation peaks
            - 'fingerprints': Generated audio fingerprints
        """
        # Load and normalize audio signal
        signal, actual_sample_rate = self.audio_loader.load_audio_ffmpeg(file_path, sample_rate)
        
        # Compute spectrogram for frequency analysis
        S_db, freqs, times = self.spectrogram_processor.compute_spectrogram(signal, actual_sample_rate)
        
        # Find peaks
        peaks = self.spectrogram_processor.find_peaks(S_db)
        
        # Generate fingerprints
        fingerprints = self.fingerprint_generator.generate_fingerprints(peaks)
        
        return {
            'file_path': file_path,
            'signal': signal,
            'sample_rate': actual_sample_rate,
            'duration': len(signal) / actual_sample_rate,
            'spectrogram': S_db,
            'freqs': freqs,
            'times': times,
            'peaks': peaks,
            'fingerprints': fingerprints
        }
        
    def process_audio_recording(self) -> Dict[str, Any]:
        """
        Record audio from the microphone and process it for identification.
        
        This method captures real-time audio from the default microphone device,
        saves it to a file, and then processes it for fingerprint generation.
        
        Returns:
            Dictionary containing comprehensive analysis results from the recorded audio,
            including the file path where the recording was saved.
        """
        print("🎤 Recording audio from microphone...")
        recorded_file_path = self.audio_recorder.record()
        print(f"📁 Recorded audio saved to: {recorded_file_path}")
        
        # Process the recorded audio file
        analysis_results = self.process_audio_file(recorded_file_path)
        analysis_results['file_path'] = recorded_file_path  # Ensure file path is included
        
        return analysis_results
    
    def add_song_to_database(self, file_path: str, title: str, artist: str = None) -> int:
        """
        Process an audio file and add it to the fingerprint database.
        
        This method performs complete audio analysis and stores both song metadata
        and generated fingerprints in the database for future identification.
        
        Args:
            file_path: Path to the audio file to process
            title: Human-readable song title
            artist: Artist name (optional, defaults to None)
            
        Returns:
            Integer song_id of the newly added song in the database
            
        Raises:
            Exception: If audio processing or database operations fail
        """
        print(f"🎵 Processing and adding song: {title}")
        
        # Perform comprehensive audio analysis
        analysis_results = self.process_audio_file(file_path)
        
        # Store song metadata in database
        song_id = self.db_manager.add_song(
            title=title,
            artist=artist,
            file_path=file_path,
            duration=analysis_results['duration']
        )
        
        # Store generated fingerprints in database
        fingerprint_count = len(analysis_results['fingerprints'])
        self.db_manager.add_fingerprints(song_id, analysis_results['fingerprints'])
        
        print(f"✅ Added song '{title}' with ID {song_id}")
        print(f"🔑 Generated {fingerprint_count:,} fingerprints")
        
        return song_id
    
    def identify_song(self, file_path: str, max_duration: float = 30.0) -> Dict[str, Any]:
        """
        Identify a song from an audio file using database matching.
        
        This method processes the query audio, generates fingerprints, and matches
        them against the database to find the most likely song match.
        
        Args:
            file_path: Path to the query audio file to identify
            max_duration: Maximum duration to process in seconds (default: 30.0)
            
        Returns:
            Dictionary containing identification results with keys:
            - 'query_file': Path to the query file
            - 'query_duration': Actual duration processed
            - 'query_fingerprints': Number of fingerprints generated
            - 'best_match_id': ID of the best matching song (None if no match)
            - 'scores': Dictionary of match scores for all candidates
            - Additional match details if a match is found
        """
        print(f"🔍 Identifying song from: {file_path}")
        
        # Process the query audio file
        analysis_results = self.process_audio_file(file_path)
        
        # Apply duration limit if specified
        if max_duration and analysis_results['duration'] > max_duration:
            max_samples = int(max_duration * analysis_results['sample_rate'])
            # Re-process with duration-limited signal
            limited_signal = analysis_results['signal'][:max_samples]
            S_db, freqs, times = self.spectrogram_processor.compute_spectrogram(
                limited_signal, analysis_results['sample_rate'])
            peaks = self.spectrogram_processor.find_peaks(S_db)
            fingerprints = self.fingerprint_generator.generate_fingerprints(peaks)
            processed_duration = max_duration
        else:
            fingerprints = analysis_results['fingerprints']
            processed_duration = analysis_results['duration']
        
        # Perform database matching
        best_song_id, match_scores = self.db_manager.match_query(fingerprints)
        
        # Compile identification results
        identification_result = {
            'query_file': file_path,
            'query_duration': processed_duration,
            'query_fingerprints': len(fingerprints),
            'best_match_id': best_song_id,
            'scores': match_scores
        }
        
        # Add detailed match information if a song was identified
        if best_song_id:
            match_details = self.db_manager.get_match_details(best_song_id, match_scores)
            identification_result.update(match_details)
        
        return identification_result
    
    def visualize_analysis(self, analysis_results: Dict[str, Any], title_prefix: str = "", 
                          save_spectrogram: Optional[str] = None, 
                          save_peaks: Optional[str] = None,
                          save_combined: Optional[str] = None) -> None:
        """
        Generate and save visualization plots for audio analysis results.
        
        This method creates various plots to visualize the audio processing pipeline,
        including spectrograms, peak detection results, and combined analyses.
        
        Args:
            analysis_results: Complete analysis results from process_audio_file()
            title_prefix: Text prefix for plot titles (default: "")
            save_spectrogram: Path to save spectrogram plot (optional)
            save_peaks: Path to save peaks-only plot (optional)
            save_combined: Path to save combined analysis plot (optional)
        """
        if save_spectrogram:
            self.visualizer.plot_spectrogram(
                analysis_results['spectrogram'], 
                analysis_results['freqs'], 
                analysis_results['times'],
                title=f"{title_prefix} Spectrogram",
                save_path=save_spectrogram
            )
        
        if save_peaks:
            self.visualizer.plot_peaks_only(
                analysis_results['freqs'], 
                analysis_results['times'], 
                analysis_results['peaks'],
                title=f"{title_prefix} Peaks",
                save_path=save_peaks
            )
        
        if save_combined:
            self.visualizer.plot_combined_analysis(
                analysis_results['spectrogram'],
                analysis_results['freqs'],
                analysis_results['times'],
                analysis_results['peaks'],
                title=f"{title_prefix} Combined Analysis",
                save_path=save_combined
            )
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive statistics about the fingerprint database.
        
        This method provides detailed information about the current state
        of the database, including song counts, fingerprint totals, and
        individual song listings.
        
        Returns:
            Dictionary containing database statistics with keys:
            - 'total_songs': Total number of songs in database
            - 'total_fingerprints': Total number of fingerprints stored
            - 'songs': List of all songs with metadata
        """
        # Get list of all songs with metadata
        songs_list = self.db_manager.list_songs()
        
        # Get total fingerprint count from database
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Fingerprints")
            total_fingerprint_count = cursor.fetchone()[0]
        
        return {
            'total_songs': len(songs_list),
            'total_fingerprints': total_fingerprint_count,
            'songs': songs_list
        }
