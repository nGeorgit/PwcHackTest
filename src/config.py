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
RESCUER_LAT = float(os.getenv("RESCUER_LAT", 38.0417850)) 
RESCUER_LON = float(os.getenv("RESCUER_LON", 23.995306))

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

# Ranking API
RANKING_API_URL = os.getenv("RANKING_API_URL")

# Azure Blob Storage Connection String
STORAGE_CONN_STRING = os.getenv("STORAGE_CONN_STRING")

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