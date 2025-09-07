"""
Configuration settings for the Shazam Clone system.

This module contains all configurable parameters for the audio
identification system including paths, processing parameters,
and system settings.
"""

import os

# Project Structure
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
MUSIC_DIR = os.path.join(PROJECT_ROOT, "music")
TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")

# Database Configuration
DATABASE_PATH = os.path.join(DATA_DIR, "shazam_clone.db")

# Audio processing settings
AUDIO_CONFIG = {
    'default_sample_rate': 22050,
    'fft_size': 2048,
    'hop_length': 512,
    'db_floor': -80
}

# Peak detection settings
PEAK_CONFIG = {
    'neighborhood_size': (20, 20),
    'threshold_db': -50
}

# Fingerprinting settings
FINGERPRINT_CONFIG = {
    'fan_value': 5,
    'target_zone': (1, 20)  # (min_delta_t, max_delta_t)
}

# Database settings
DATABASE_CONFIG = {
    'db_path': DATABASE_PATH,
    'enable_wal_mode': True  # For better concurrent access
}

# Visualization settings
VISUALIZATION_CONFIG = {
    'default_figsize': (12, 6),
    'dpi': 150,
    'spectrogram_cmap': 'magma',
    'peak_color': 'black',
    'peak_size': 2
}

# Performance settings
PERFORMANCE_CONFIG = {
    'max_query_duration': 30.0,  # seconds
    'batch_size_fingerprints': 1000
}

# Output Configuration
RECORDED_AUDIO_PATH = os.path.join(OUTPUT_DIR, "recorded_audio.wav")

# Supported Audio Formats
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}

# Processing Configuration
BATCH_SIZE = 10000
PROGRESS_UPDATE_INTERVAL = 100000

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [DATA_DIR, OUTPUT_DIR, MUSIC_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
