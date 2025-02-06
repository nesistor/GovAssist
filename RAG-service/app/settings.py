import os
from google.cloud import firestore

# Load environment variables
OPENAI_EMBEDDING_API_KEY = os.getenv("OPENAI_EMBEDDING_API_KEY")
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID")

# Initialize Firestore client
db = firestore.Client(project=FIRESTORE_PROJECT_ID)

# OpenAI API settings
OPENAI_API_BASE = "https://api.x.ai/v1"
OPENAI_MODEL = "v1"  # Ensure correct model ID
