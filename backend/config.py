"""
Configuration settings for the PDF Extraction Backend
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model settings
YOLO_MODEL = "yolov8n.pt"  # Will download automatically
CONFIDENCE_THRESHOLD = 0.5

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp'}

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
