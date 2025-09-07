"""
Spectrogram Processing Module - Advanced Audio Analysis

This module provides high-performance spectrogram computation and peak detection
algorithms optimized for audio fingerprinting applications. It implements
efficient FFT-based analysis with configurable parameters for optimal
audio identification performance.

Key Features:
- High-performance FFT-based spectrogram computation
- Advanced peak detection with local maxima filtering
- Configurable window functions and analysis parameters
- Optimized stride tricks for efficient memory usage
- Decibel scaling with floor limiting for robust analysis

Dependencies:
- NumPy for numerical computing and FFT operations
- NumPy stride tricks for efficient array operations

Author: Hocus Pocus Project
Version: 1.0
"""

import numpy as np
from numpy.lib.stride_tricks import as_strided
from typing import Tuple, List, Callable


class SpectrogramProcessor:
    """
    Advanced spectrogram computation and peak detection for audio fingerprinting.
    
    This class provides optimized algorithms for converting audio signals into
    spectrograms and extracting prominent peaks that serve as the foundation
    for audio fingerprinting and identification.
    """
    
    def __init__(self, fft_size: int = 2048, hop_length: int = 512, 
                 window_fn: Callable = np.hanning, db_floor: float = -80.0):
        """
        Initialize the spectrogram processor with analysis parameters.
        
        Args:
            fft_size: Size of the FFT window for frequency analysis (default: 2048)
            hop_length: Number of samples between successive frames (default: 512)
            window_fn: Window function to apply before FFT (default: Hanning window)
            db_floor: Minimum dB value for dynamic range limiting (default: -80.0)
        """
        self.fft_size = fft_size
        self.hop_length = hop_length
        self.window_function = window_fn
        self.decibel_floor = db_floor
    
    def compute_spectrogram(self, signal: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute high-quality spectrogram from audio signal using FFT analysis.
        
        This method performs Short-Time Fourier Transform (STFT) to convert
        the time-domain audio signal into a time-frequency representation
        suitable for peak detection and fingerprinting.
        
        Args:
            signal: Normalized audio signal array (typically float64)
            sample_rate: Audio sample rate in Hz
            
        Returns:
            Tuple containing:
            - spectrogram_db: Magnitude spectrogram in decibels
            - frequencies: Frequency bin centers in Hz
            - times: Time frame centers in seconds
        """
        if len(signal) < self.fft_size:
            raise ValueError(f"Signal too short ({len(signal)}) for FFT size ({self.fft_size})")
        
        # Prepare analysis window
        analysis_window = self.window_function(self.fft_size)
        
        # Calculate number of analysis frames
        num_frames = 1 + (len(signal) - self.fft_size) // self.hop_length
        
        # Initialize spectrogram matrix (frequency bins x time frames)
        spectrogram_magnitude = np.zeros((self.fft_size // 2 + 1, num_frames))

        # Process each time frame with FFT analysis
        for frame_index in range(num_frames):
            start_sample = frame_index * self.hop_length
            end_sample = start_sample + self.fft_size
            
            # Extract frame
            audio_frame = signal[start_sample:end_sample]
            if len(audio_frame) < self.fft_size:
                audio_frame = np.pad(audio_frame, (0, self.fft_size - len(audio_frame)))

            # Apply window function and compute FFT
            windowed_frame = audio_frame * analysis_window
            frequency_spectrum = np.fft.rfft(windowed_frame)
            magnitude_spectrum = np.abs(frequency_spectrum)
            spectrogram_magnitude[:, frame_index] = magnitude_spectrum

        # Convert to dB scale
        spectrogram_db = 20 * np.log10(spectrogram_magnitude + 1e-10)
        spectrogram_db = np.maximum(spectrogram_db, self.decibel_floor)

        # Generate axes
        frequency_bins = np.fft.rfftfreq(self.fft_size, d=1.0/sample_rate)
        time_frames = np.arange(num_frames) * self.hop_length / sample_rate

        return spectrogram_db, frequency_bins, time_frames

    @staticmethod
    def maximum_filter(array: np.ndarray, filter_size: Tuple[int, int]) -> np.ndarray:
        """
        Apply maximum filter for efficient local maxima detection.
        
        This method uses NumPy stride tricks to implement a sliding window
        maximum filter, which is essential for identifying local peaks
        in the spectrogram for fingerprinting.
        
        Args:
            array: Input 2D array (typically spectrogram)
            filter_size: Filter window dimensions (freq_window, time_window)
            
        Returns:
            Filtered array with local maxima preserved
        """
        freq_window, time_window = filter_size
        freq_dim, time_dim = array.shape
        
        # Create sliding window view using stride tricks
        output_shape = (freq_dim - freq_window + 1, time_dim - time_window + 1, freq_window, time_window)
        output_strides = array.strides + array.strides
        sliding_windows = as_strided(array, shape=output_shape, strides=output_strides)
        
        # Find maximum in each window
        filtered_result = np.max(sliding_windows, axis=(2, 3))
        
        # Apply padding to maintain original array dimensions
        freq_pad = (freq_window - 1) // 2
        time_pad = (time_window - 1) // 2
        padded_result = np.pad(
            filtered_result, 
            ((freq_pad, freq_window - 1 - freq_pad), (time_pad, time_window - 1 - time_pad)), 
            mode='edge'
        )
        
        return padded_result

    def find_peaks(self, spectrogram_db: np.ndarray, 
                   neighborhood_size: Tuple[int, int] = (20, 20), 
                   threshold_db: float = -50.0) -> List[Tuple[int, int]]:
        """
        Identify prominent peaks in spectrogram for constellation map generation.
        
        This method finds local maxima in the spectrogram that exceed both
        a neighborhood criterion and an absolute threshold, forming the
        basis for audio fingerprinting.
        
        Args:
            spectrogram_db: Magnitude spectrogram in decibel scale
            neighborhood_size: Local maxima window size (freq_bins, time_frames)
            threshold_db: Minimum decibel threshold for peak detection
            
        Returns:
            List of peak coordinates as (time_index, freq_index) tuples
        """
        # CPU implementation
        local_maxima = self.maximum_filter(spectrogram_db, neighborhood_size)
        peak_mask = (spectrogram_db == local_maxima) & (spectrogram_db > threshold_db)
        peak_coordinates = np.argwhere(peak_mask)
        
        # Convert to (time, frequency) format
        peak_list = [(time_idx, freq_idx) for freq_idx, time_idx in peak_coordinates]
        
        return peak_list
