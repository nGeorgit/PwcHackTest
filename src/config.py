import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
PAGE_CONFIG = {
    "layout": "wide",
    "page_title": "RescuerAI - Emergency Command",
    "page_icon": "🚑"
}

# Default Locations
# Use environment variables if available, otherwise fallback to defaults
DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", 40.6401))
DEFAULT_LON = float(os.getenv("DEFAULT_LON", 22.9444))
RESCUER_LAT = float(os.getenv("RESCUER_LAT", 40.6350))
RESCUER_LON = float(os.getenv("RESCUER_LON", 22.9400))

# Custom CSS
CUSTOM_CSS = """
<style>
    .reportview-container {
        background: #0e1117;
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .urgent {
        color: #ff4b4b;
        font-weight: bold;
    }
</style>
"""
