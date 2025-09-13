# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Securely load the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Database Configuration ---
MASTER_DB_PATH = "data/master_reviews.db"

# --- Analysis Configuration ---
# Define the apps you want to analyze. The pipeline will scrape data for these apps.
APPS_TO_ANALYZE = [
    {
        "app_name": "Zomato",
        "app_id": "com.application.zomato",
        "output_dir": "output/zomato_report"
    },
    {
        "app_name": "Swiggy",
        "app_id": "in.swiggy.android",
        "output_dir": "output/swiggy_report"
    },
    {
        "app_name": "Blinkit",
        "app_id": "com.grofers.customerapp",
        "output_dir": "output/blinkit_report"
    }
]
