from fastapi import HTTPException, Request
from firebase_admin import auth
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import firebase_admin
from firebase_admin import credentials
import os

# Initialize Firebase Admin SDK
firebase_cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
firebase_admin.initialize_app(firebase_cred)

class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract token from Authorization header
        token = request.headers.get("Authorization")

        if not token:
            raise HTTPException(status_code=403, detail="Authorization token missing")

        # Remove "Bearer " from the token string
        token = token.replace("Bearer ", "")

        try:
            # Verify the token with Firebase
            decoded_token = auth.verify_id_token(token)
            request.state.user = decoded_token  # Store decoded user info in request state
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")

        # Call the next middleware or endpoint
        response = await call_next(request)
        return response