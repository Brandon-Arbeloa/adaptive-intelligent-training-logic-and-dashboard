import os
from dotenv import load_dotenv
from pathlib import Path

# Get the base directory (parent of backend folder)
BASE_DIR = Path(__file__).parent.parent

# Load .env from the base directory
load_dotenv(BASE_DIR / '.env')

SPREADSHEET_URL = os.getenv("SPREADSHEET_URL")
CRED_PATH = str(BASE_DIR / "credentials.json")  # Use the credentials.json in the main folder
REPORT_SHEET = os.getenv("REPORT_SHEET_NAME", "Rotation Report")
WEEK_SHEETS = [s.strip() for s in os.getenv("WEEK_SHEETS", "Week 1,Week 2,Week 3,Week 4,Week 5,Week 6,Week 7,Week 8").split(",")]
OVERUSED = int(os.getenv("OVERUSED", "4"))
BALANCED_MIN = int(os.getenv("BALANCED_MIN", "2"))
LOG_PATH = str(BASE_DIR / "logs" / "rotation.log")