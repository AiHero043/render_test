"""
Configuration file for EROME automation system
Edit these values to customize your automation workflow
"""
import os
from pathlib import Path

# ========== DATABASE SETTINGS ==========
# PostgreSQL database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///profiles.db')

# ========== DIRECTORY PATHS ==========
# Local directories
DOWNLOAD_DIR = Path(r"D:\projects\freelance\data\drive_downloads")
# TEMP_DIR = Path(r"D:\projects\freelance\data\Temp")
# MEDIA_POOL_DIR = Path(r"C:\Users\UKGC\Desktop\MediaPool") # contains images and videos downloaded from gdrive
OUTPUT_DIR = Path(r"D:\projects\freelance\data\Posts") # output folder after sorting images and videos into posts 2 images 1 video
RENEWED_IMAGES_DIR = Path(r"D:\projects\freelance\data\Batch\_renewed")
RENEWED_VIDEOS_DIR = Path(r"D:\projects\freelance\data\Batch\VIDEOS")

# ========== GOOGLE DRIVE SETTINGS ==========
GOOGLE_DRIVE_DOWNLOAD_FOLDER_ID = "1orLexTWIjg2jDGAfULwvJbRlnCU4cZF_"  # Folder ID to download source content from
GOOGLE_DRIVE_UPLOAD_FOLDER_ID = "1orLexTWIjg2jDGAfULwvJbRlnCU4cZF_"  # Folder ID to upload processed posts to
CREDENTIALS_FILE = Path("credentials.json")  # Google API credentials file
TOKEN_FILE = Path("token.pickle")  # OAuth token cache

# Download specific post folders (e.g., "post 1" to "post 10")
DOWNLOAD_POST_START = 1    # Starting post number to download
DOWNLOAD_POST_END = 10     # Ending post number to download (None = download all files/folders)

# ========== POST MANAGEMENT ==========
CURRENT_POST_NUMBER = 360  # Starting post number (will be updated automatically)
SET_VALUE = 360  # Trigger renewal every X posts
MAX_POST = 10000  # Maximum post number before resetting

# ========== IMAGE PROCESSING (IMAGEMAGICK)==========
# IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.2-Q16\magick.exe"  # Path to ImageMagick
IMAGEMAGICK_PATH = r"D:\softwares\ImageMagick-7.1.2-Q16-HDRI\magick.exe"  # Path to ImageMagick
IMAGE_QUALITY_MIN = 85  # Minimum image quality (85-99)
IMAGE_QUALITY_MAX = 99  # Maximum image quality (85-99)
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# ========== VIDEO PROCESSING (HANDBRAKE) ==========
# HANDBRAKE_CLI_PATH = r"C:\Program Files\HandBrake\HandBrakeCLI.exe"  # Path to HandBrakeCLI.exe
HANDBRAKE_CLI_PATH = r"D:\softwares\handbrake\HandBrakeCLI.exe"  # Path to HandBrakeCLI.exe
VIDEO_RF_MIN = 17.5  # Minimum RF quality (lower = better quality, bigger file)
VIDEO_RF_MAX = 29  # Maximum RF quality (higher = lower quality, smaller file)
VIDEO_ENCODER_PRESETS = ["veryfast", "faster", "fast", "medium", "slow"]  # Random encoder speeds
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".webm", ".flv", ".3gp", ".mpeg", ".mpg"}

# ========== POST COMPOSITION ==========
IMAGES_PER_POST = 2  # Number of images per post
VIDEOS_PER_POST = 1  # Number of videos per post

# ========== AUTOMATION SETTINGS ==========
STATE_FILE = Path("automation_state.json")  # Tracks current state
LOG_FILE = Path("automation_log.txt")  # Log file for automation
DELETE_SOURCE_AFTER_UPLOAD = False  # Delete original files from Google Drive after processing and uploading

# ========== WEBHOOK/TRIGGER SETTINGS (OPTIONAL) ==========
WEBHOOK_URL = ""  # Optional: URL to call after successful upload
ENABLE_WEBHOOK = False  # Set to True to enable webhook notifications
