from fastapi import APIRouter, Request, HTTPException, UploadFile
from typing import List
from api.services.openai_service import process_image_with_grok, process_document_with_text_model, generate_response
from api.utils.image_utils import encode_image_to_base64, convert_pdf_to_images, pil_image_to_base64
from api.models.document_models import DocumentCheckResult, QuestionRequest, DocumentRequest, DocumentResponse, FunctionCallResultMessage
import tempfile
import logging

router = APIRouter()

# Function to get user data from request state
def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user

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

@router.post("/generate-response", response_model=str)
def ask_question(request: Request, request_data: QuestionRequest):
    user = get_current_user(request)  # Access the user from request state
    session_id = user["uid"]  # Use Firebase UID as the session identifier

    try:
        logger.debug(f"User ID: {user['uid']}, Received request data: {request_data}")

        response = generate_response(request_data.dict(), session_id)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")