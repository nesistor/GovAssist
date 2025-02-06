import os
from google.cloud import firestore

# Load environment variables
XAI_API_KEY = os.getenv("XAI_API_KEY")
AIML_API_KEY = os.getenv("AIML_API_KEY")
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID")

# Initialize Firestore client
db = firestore.Client(project=FIRESTORE_PROJECT_ID)

# OpenAI API settings
XAI_API_BASE = "https://api.x.ai/v1"
XAI_MODEL = "v1" 

AIML_API_BASE = "https://api.openai.com/v1"
