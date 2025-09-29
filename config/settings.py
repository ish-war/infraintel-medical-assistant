import os
from dotenv import load_dotenv

load_dotenv()

# Load .env from main folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # config folder path
MAIN_DIR = os.path.dirname(BASE_DIR)  # intraintel folder
load_dotenv(os.path.join(MAIN_DIR, ".env"))

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
PROCESSOR_ID = os.getenv("GCP_PROCESSOR_ID")
LOCATION = os.getenv("GCP_LOCATION", "us")

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
OUTPUT_BUCKET = os.getenv("GCS_OUTPUT_BUCKET")

GCS_INPUT_URI = f"gs://{BUCKET_NAME}/"
GCS_OUTPUT_URI = f"gs://{OUTPUT_BUCKET}/"

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Google API key for embeddings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
