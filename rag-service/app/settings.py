# settings.py
import os
from google.cloud import firestore

# Load environment variables
XAI_API_KEY = os.getenv("XAI_API_KEY")
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Validate environment variables
if not all([XAI_API_KEY, FIRESTORE_PROJECT_ID, GOOGLE_CREDENTIALS_PATH]):
    raise ValueError("Missing required environment variables")

# Initialize Firestore
db = firestore.Client(project=FIRESTORE_PROJECT_ID)

# OpenAI configuration
XAI_API_BASE = "https://api.x.ai/v1"
XAI_MODEL = "v1"