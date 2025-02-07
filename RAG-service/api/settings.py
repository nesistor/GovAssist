import os
from google.cloud import firestore

# Load environment variables
XAI_API_KEY = os.getenv("XAI_API_KEY")
AIML_API_KEY = os.getenv("AIML_API_KEY")
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Check if FIRESTORE_PROJECT_ID is set
if not FIRESTORE_PROJECT_ID:
    raise ValueError("FIRESTORE_PROJECT_ID is not set in environment variables.")

# Ensure that GOOGLE_APPLICATION_CREDENTIALS is set
if not GOOGLE_CREDENTIALS_PATH:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

# Initialize Firestore client
db = firestore.Client(project=FIRESTORE_PROJECT_ID)

# OpenAI API settings
XAI_API_BASE = "https://api.x.ai/v1"
XAI_MODEL = "v1" 

AIML_API_BASE = "https://api.aimlapi.com/v1"
