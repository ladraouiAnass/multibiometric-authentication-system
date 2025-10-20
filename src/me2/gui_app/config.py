"""Configuration Settings for Biometric Authentication System

Centralized configuration for paths, URLs, and system parameters.
Update these paths according to your deployment environment.
"""

import os
from pathlib import Path

# Base project paths - Update these for your environment
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ME2_DIR = SRC_DIR / "me2"

# Dataset and model paths
dataset = str(PROJECT_ROOT / "data")
voices = "/voices"
faces = "/faces"

# Cache directories
cache_camera = str(SRC_DIR / "cache" / "camera")
cache_audio = str(SRC_DIR / "cache" / "audio")

# Legacy path variables (for backward compatibility)
src = str(SRC_DIR)
facespkl = str(ME2_DIR / "modele")
train_modele = str(ME2_DIR / "modele" / "train_modele.py")
me2 = str(ME2_DIR)

# Camera configuration
# Update this URL for your camera setup (IP camera, USB camera, etc.)
camurl = 'http://192.168.1.104:8080/video'  # IP camera URL
# camurl = 0  # Use this for USB camera (index 0)

# Authentication thresholds
VOICE_THRESHOLD = 0.10
FACE_CONFIDENCE = 0.6

# Recording parameters
AUDIO_SAMPLE_RATE = 44100
RECORDING_DURATION = 6.0

# Ensure cache directories exist
os.makedirs(cache_camera, exist_ok=True)
os.makedirs(cache_audio, exist_ok=True)
