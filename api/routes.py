from fastapi import APIRouter, Request, HTTPException, UploadFile, Depends 
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.session import get_async_session
from api.services.openai_service import process_image_with_grok, process_document_with_text_model, generate_response
from api.utils.image_utils import encode_image_to_base64, convert_pdf_to_images, pil_image_to_base64
from api.models.document_models import DocumentCheckResult, ConversationMessage, QuestionRequest, QuestionResponse, DocumentRequest, DocumentResponse, FunctionCallResultMessage
import tempfile
import logging

router = APIRouter()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@router.get("/initial-message", response_model=str)
def initial_message(request: Request):
    """
    Endpoint to provide an initial greeting message to the user.
    """
    user = get_current_user(request)  # Access the user from request state
    return f"Hi {user['name']}! Welcome to the Gov Assistant. How can I help you today?"

@router.get("/options", response_model=List[str])
def get_options(request: Request):
    """
    Endpoint to provide predefined options for the user.
    """
    user = get_current_user(request)  # Access the user from request state
    options = ["Drivers License", "ID", "Passport", "Something Else"]
    return options

@router.get("/conversation-history", response_model=List[ConversationMessage])
async def conversation_history(request: Request, session: AsyncSession = Depends(get_async_session)):
    """
    Pobiera historię konwersacji dla danego użytkownika.
    """
    user = await get_current_user(request)
    user_id = user["uid"]
    session_id = request.state.session_id  # Pobranie session_id z requestu

    if not user_id or not session_id:
        raise HTTPException(status_code=400, detail="Brak wymaganych parametrów: user_id lub session_id")

    try:
        history = await get_conversation_history(session, user_id, session_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas pobierania historii rozmów: {str(e)}")    

@router.get("/conversation-title")
async def get_conversation_title(request: Request):
    """
    Zwraca tytuł konwersacji dla danego użytkownika.
    """
    user = get_current_user(request)
    user_id = user["uid"]
    session_id = request.state.session_id  

    if not user_id or not session_id:
        raise HTTPException(status_code=400, detail="Brak wymaganych danych: user_id lub session_id")

    try:
        title = await generate_conversation_title(user_id, session_id)
        return {"user_id": user_id, "session_id": session_id, "title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas generowania tytułu: {str(e)}")

@router.post("/validate-document")
def validate_document(request: Request, file: UploadFile):
    user = get_current_user(request)  # Access the user from request state
    logger.debug(f"User ID: {user['uid']}, Received file: {file.filename}, content_type: {file.content_type}")

    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only JPEG, PNG, and PDF are allowed.")

    try:
        base64_images = []

        if file.content_type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_pdf:
                temp_pdf.write(file.file.read())
                temp_pdf.flush()
                images = convert_pdf_to_images(temp_pdf.name)
                base64_images = [pil_image_to_base64(image) for image in images]
        else:
            base64_image = encode_image_to_base64(file.file)
            base64_images = [base64_image]

        aggregated_results = [process_image_with_grok(base64_image) for base64_image in base64_images]
        response = process_document_with_text_model(aggregated_results)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the document: {str(e)}")

def get_current_user(request: Request):
    if request.state.user:
        return {"uid": request.state.user["uid"], "is_authenticated": True}
    return {"uid": request.state.session_id, "is_authenticated": False}

@router.post("/generate-response", response_model=QuestionResponse)
async def ask_question(request: Request, request_data: dict, session: AsyncSession = Depends(get_async_session)):
    user = get_current_user(request)

    # Check if the request asks for a new conversation
    if request_data.get("start", False):  
        session_id = str(uuid.uuid4())  # Generate a new session ID
        logger.info(f"New conversation started. New Session ID: {session_id}")
    else:
        session_id = user["uid"]  # Use existing session ID

    question = request_data.get("question")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    logger.debug(f"User {session_id} asked: {question}")

    try:
        response_message = await generate_response(request_data, session_id)
        logger.debug(f"Response returned: {response_message}")

        return QuestionResponse(response=response_message, session_id=session_id)  # Return new session ID if changed

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")