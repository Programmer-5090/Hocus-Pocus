"""
Audio recording module for real-time microphone capture.

This module provides functionality for capturing high-quality audio
from the system microphone for audio identification purposes.

Author: Hocus Pocus Project
Version: 1.0
"""

import pyaudio
import wave
from typing import Optional


class AudioRecorder:
    """
    High-quality audio recorder for microphone input capture.
    
    This class provides a simple interface for recording audio from the
    system's default microphone with configurable quality settings
    optimized for audio fingerprinting and identification.
    """
    
    def __init__(self, filename: str, duration: int = 15, 
                 sample_rate: int = 22050, channels: int = 1):
        """
        Initialize the audio recorder with specified parameters.
        
        Args:
            filename: Output file path for the recorded audio (WAV format).
            duration: Recording duration in seconds. Default is 15 seconds
                     which provides good balance between accuracy and speed.
            sample_rate: Audio sample rate in Hz. 22050 Hz is optimal for
                        audio identification as it captures frequencies up to ~11kHz.
            channels: Number of audio channels. Mono (1) is recommended for
                     fingerprinting as it reduces data size and processing time.
        """
        self.filename = filename
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = 1024  # Buffer size for audio streaming
        self.format = pyaudio.paInt16  # 16-bit audio for good quality/size balance

    def record(self) -> str:
        """
        Record audio from the default microphone and save to WAV file.
        
        This method captures audio in real-time, providing user feedback
        during the recording process. The recorded audio is automatically
        saved in WAV format for compatibility with the audio processing pipeline.
        
        Returns:
            str: Path to the saved audio file.
            
        Raises:
            RuntimeError: If audio recording fails due to microphone issues
                         or insufficient system resources.
            
        Note:
            Ensure your microphone is connected and not being used by other
            applications before calling this method.
        """
        audio_interface = None
        stream = None
        
        try:
            # Initialize PyAudio interface
            audio_interface = pyaudio.PyAudio()
            
            # Configure audio stream for recording
            stream = audio_interface.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            print(f"🎤 Recording audio for {self.duration} seconds...")
            
            # Calculate total number of chunks needed
            total_chunks = int(self.sample_rate / self.chunk_size * self.duration)
            audio_frames = []
            
            # Record audio in chunks
            for chunk_num in range(total_chunks):
                try:
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_frames.append(audio_data)
                except IOError as e:
                    print(f"⚠️  Warning: Audio buffer overflow (chunk {chunk_num}): {e}")
                    continue

            print("✅ Recording completed successfully.")

        except Exception as e:
            raise RuntimeError(f"Failed to record audio: {e}")
            
        finally:
            # Clean up audio resources
            if stream:
                stream.stop_stream()
                stream.close()
            if audio_interface:
                audio_interface.terminate()

        # Save recorded audio to WAV file
        self._save_audio_file(audio_frames, audio_interface)
        
        print(f"💾 Audio saved to: {self.filename}")
        return self.filename
    
    def _save_audio_file(self, audio_frames: list, audio_interface: pyaudio.PyAudio) -> None:
        """
        Save recorded audio frames to a WAV file.
        
        Args:
            audio_frames: List of audio data chunks from recording.
            audio_interface: PyAudio instance for getting sample width.
        """
        try:
            with wave.open(self.filename, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(audio_interface.get_sample_size(self.format))
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(b''.join(audio_frames))
                
        except Exception as e:
            raise RuntimeError(f"Failed to save audio file: {e}")