"""
Audio Loading Module - Multi-Format Audio File Processing

This module provides comprehensive audio loading capabilities for the Shazam clone
system, supporting various audio formats through FFmpeg integration and native
Python libraries for high-quality audio processing.

Key Features:
- Multi-format support (WAV, MP3, FLAC, M4A, etc.)
- FFmpeg integration for format conversion
- Native WAV processing with proper bit-depth handling
- Automatic audio normalization and type conversion
- Error handling for corrupted or unsupported files

Dependencies:
- FFmpeg (external tool for format conversion)
- NumPy for numerical array processing
- Python wave module for native WAV support

Author: Hocus Pocus Project
Version: 1.0
"""

import numpy as np
import wave
import subprocess
from typing import Tuple, Optional


class AudioLoader:
    """
    Professional audio loading system with multi-format support.
    
    This class provides robust audio file loading capabilities, handling
    various audio formats through FFmpeg conversion and native Python
    libraries for optimal audio processing quality.
    """
    
    @staticmethod
    def load_wav(path: str) -> Tuple[np.ndarray, int]:
        """
        Load WAV file using native Python wave module with proper bit-depth handling.
        
        This method provides direct WAV file loading without external dependencies,
        ensuring accurate audio data extraction with proper normalization for
        different bit depths (8-bit, 16-bit, 32-bit).
        
        Args:
            path: Absolute or relative path to the WAV file
            
        Returns:
            Tuple containing:
            - signal: Normalized float64 audio array in range [-1.0, 1.0]
            - sample_rate: Audio sample rate in Hz
            
        Raises:
            FileNotFoundError: If the specified WAV file doesn't exist
            ValueError: If the audio format is unsupported or corrupted
        """
        try:
            with wave.open(path, 'rb') as wf:
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                num_frames = wf.getnframes()
                raw_audio_data = wf.readframes(num_frames)

        except wave.Error as e:
            raise ValueError(f"Error reading WAV file '{path}': {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"WAV file not found: {path}")

        # Convert byte data to numpy array with appropriate data type
        if sample_width == 1:  # 8-bit unsigned audio
            audio_dtype = np.uint8
        elif sample_width == 2:  # 16-bit signed audio
            audio_dtype = np.int16
        elif sample_width == 4:  # 32-bit signed audio
            audio_dtype = np.int32
        else:
            raise ValueError(f"Unsupported sample width: {sample_width} bytes")

        # Convert raw bytes to NumPy array with appropriate data type
        audio_signal = np.frombuffer(raw_audio_data, dtype=audio_dtype)

        # Convert stereo to mono by taking only the first channel
        if num_channels > 1:
            audio_signal = audio_signal[::num_channels]

        # Normalize audio to floating-point range [-1.0, 1.0] based on bit depth
        if sample_width == 1:  # 8-bit unsigned: [0, 255] -> [-1, 1]
            normalized_signal = (audio_signal - 128) / 128.0
        elif sample_width == 2:  # 16-bit signed: [-32768, 32767] -> [-1, 1]
            normalized_signal = audio_signal / float(2**(8 * sample_width - 1))
        elif sample_width == 4:  # 32-bit signed: [-2^31, 2^31-1] -> [-1, 1]
            normalized_signal = audio_signal / float(2**(8 * sample_width - 1))
        else:
            raise ValueError(f"Unsupported sample width for normalization: {sample_width} bytes")

        return normalized_signal.astype(np.float64), sample_rate

    @staticmethod
    def load_audio_ffmpeg(path: str, sample_rate: int = 22050) -> Tuple[np.ndarray, int]:
        """
        Load audio using FFmpeg with support for multiple formats and resampling.
        
        This method leverages FFmpeg's comprehensive format support to load
        audio files (MP3, FLAC, M4A, etc.) and automatically converts them
        to a standardized format suitable for audio fingerprinting.
        
        Args:
            path: Path to the audio file (supports WAV, MP3, FLAC, M4A, etc.)
            sample_rate: Desired output sample rate in Hz (default: 22050)
            
        Returns:
            Tuple containing:
            - signal: Normalized float32 audio array in range [-1.0, 1.0]
            - sample_rate: Actual sample rate used (matches input parameter)
            
        Raises:
            RuntimeError: If FFmpeg is not installed or accessible
            FileNotFoundError: If the specified audio file doesn't exist
            subprocess.CalledProcessError: If FFmpeg conversion fails
        """
        try:
            # Construct FFmpeg command for high-quality audio conversion
            ffmpeg_command = [
                "ffmpeg",
                "-i", path,                    # Input file path
                "-f", "f32le",                 # Output format: 32-bit float little-endian
                "-ac", "1",                    # Convert to mono (1 audio channel)
                "-ar", str(sample_rate),       # Resample to target sample rate
                "-y",                          # Overwrite output without asking
                "pipe:1"                       # Send output to stdout pipe
            ]

            # Execute FFmpeg with subprocess
            ffmpeg_process = subprocess.Popen(
                ffmpeg_command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL  # Suppress FFmpeg verbose output
            )
            
            # Read raw audio data from FFmpeg output
            raw_audio_bytes = ffmpeg_process.stdout.read()
            return_code = ffmpeg_process.wait()
            
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, ffmpeg_command)

            # Convert bytes to float32 NumPy array (already normalized by FFmpeg)
            audio_signal = np.frombuffer(raw_audio_bytes, dtype=np.float32)
            
            return audio_signal, sample_rate
            
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found in system PATH. Please install FFmpeg:\n"
                "1. Download from https://ffmpeg.org/download.html\n"
                "2. Add FFmpeg to your system PATH\n"
                "3. Restart your terminal/IDE\n"
                "Alternatively, use WAV files with the load_wav() method."
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed to process '{path}': {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading audio file '{path}': {e}")
