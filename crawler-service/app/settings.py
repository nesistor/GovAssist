import os

OPENAI_API_KEY = os.getenv("OPENAI_KEY")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4") 

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "path/to/your/firebase_credentials.json")
