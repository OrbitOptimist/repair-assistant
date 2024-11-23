"""
Configuration settings for the Repair Assistant.
Copy this file to config.py and update with your settings.
"""
import os

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Camera Settings
CAMERA_INDEX = 0  # Default camera (usually built-in webcam)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Text-to-Speech Settings
TTS_RATE = 150  # Words per minute
TTS_VOLUME = 1.0  # Range 0.0 to 1.0

# Application Settings
DEBUG_MODE = False
LOG_LEVEL = "INFO"
DOCS_PATH = "docs"  # Directory containing repair documentation