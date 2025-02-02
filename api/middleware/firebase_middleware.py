import logging
import os
import uuid
from firebase_admin import auth, credentials, initialize_app
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
if not FIREBASE_CREDENTIALS_PATH:
    logger.critical("Zmienna środowiskowa FIREBASE_CREDENTIALS_PATH nie jest ustawiona!")
    raise RuntimeError("Brak ścieżki do kredensjałów Firebase!")

logger.info(f"Używamy kredensjałów Firebase z: {FIREBASE_CREDENTIALS_PATH}")

try:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    initialize_app(cred)
    logger.info("Firebase Admin SDK został pomyślnie zainicjowany")
except Exception as e:
    logger.critical(f"Błąd inicjalizacji Firebase: {e}", exc_info=True)
    raise RuntimeError("Błąd podczas inicjalizacji Firebase")

class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug("Przetwarzanie zapytania w middleware")
        
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split("Bearer ")[-1]
            try:
                decoded_token = auth.verify_id_token(token)
                request.state.user = decoded_token
                request.state.session_id = decoded_token["uid"]
                logger.info(f"Użytkownik {decoded_token['uid']} pomyślnie zautoryzowany")
            except Exception as e:
                logger.error(f"Błąd weryfikacji tokenu: {e}")
                raise HTTPException(status_code=401, detail="Błędny token lub token wygasł")
        else:
            request.state.user = None
            request.state.session_id = str(uuid.uuid4())  # Generowanie unikalnego session_id
            logger.info(f"Sesja gościa: {request.state.session_id}")

        return await call_next(request)
