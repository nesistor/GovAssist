import logging
from firebase_admin import auth
from fastapi import Request, HTTPException, status

logger = logging.getLogger(__name__)

def get_user_name_from_firebase(uid: str) -> str:
    try:
        user_record = auth.get_user(uid)
        return user_record.display_name if user_record.display_name else "citizen"
    except Exception as e:
        logger.error(f"Error fetching user name for uid {uid}: {e}")
        return "citizen"


def get_current_user_uid(request: Request) -> str:
    """
    Pobiera UID użytkownika na podstawie tokena autoryzacyjnego w nagłówku Authorization.
    
    Oczekuje nagłówka w formacie: "Bearer <token>". Jeśli token jest nieprawidłowy,
    zwraca wyjątek HTTP 401.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak nagłówka Authorization."
        )
    
    # Nagłówek powinien mieć format "Bearer <token>"
    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy format nagłówka Authorization."
        )
    
    token = parts[1]
    
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token.get("uid")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nie znaleziono UID w tokenie."
            )
        return uid
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy token."
        ) from e
