import firebase_admin
from firebase_admin import credentials, storage, firestore
import logging
import os

logger = logging.getLogger(__name__)

# Inicjalizacja Firebase
cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})

db = firestore.client()
bucket = storage.bucket()

class DocumentManager:
    @staticmethod
    async def save_document(session_id: str, file_data: bytes, analysis_data: dict):
        try:
            # Zapisz plik PDF w Storage
            blob = bucket.blob(f"documents/{session_id}.pdf")
            blob.upload_from_string(file_data, content_type='application/pdf')
            
            # Zapisz metadane w Firestore
            doc_ref = db.collection("document_analysis").document(session_id)
            doc_ref.set({
                "fields": analysis_data['fields'],
                "pdf_url": blob.public_url,
                "status": "analyzed"
            })
            
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Błąd zapisu do Firebase: {str(e)}")
            raise

    @staticmethod
    async def get_document_analysis(session_id: str):
        try:
            doc_ref = db.collection("document_analysis").document(session_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            return doc.to_dict()
            
        except Exception as e:
            logger.error(f"Błąd pobierania analizy: {str(e)}")
            raise