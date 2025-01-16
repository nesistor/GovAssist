from fastapi import APIRouter, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
from api.services.openai_service import process_image_with_grok, process_document_with_text_model, generate_response
from api.utils.image_utils import encode_image_to_base64, convert_pdf_to_images, pil_image_to_base64
from api.models.document_models import DocumentCheckResult, QuestionRequest, DocumentRequest, DocumentResponse, FunctionCallResultMessage
import tempfile
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/initial-message", response_model=str)
def initial_message():
    """
    Endpoint to provide an initial greeting message to the user.
    """
    return "Hi there! Welcome to the Gov Assistant. How can I help you today?"

@router.get("/options", response_model=List[str])
def get_options():
    """
    Endpoint to provide predefined options for the user.
    """
    options = ["Drivers License", "ID", "Passport", "Something Else"]
    return options

# API endpoint for document validation
@router.post("/validate-document")
def validate_document(file: UploadFile):
    logger.debug(f"Received file: {file.filename}, content_type: {file.content_type}")
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only JPEG, PNG, and PDF are allowed.")

    try:
        base64_images = []

        if file.content_type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_pdf:
                temp_pdf.write(file.file.read())
                temp_pdf.flush()
                images = convert_pdf_to_images(temp_pdf.name)
                logger.debug(f"Converted PDF to {len(images)} images.")
                base64_images = [pil_image_to_base64(image) for image in images]
        else:
            base64_image = encode_image_to_base64(file.file)
            base64_images = [base64_image]

        # Process image with Grok Vision Model
        aggregated_results = [process_image_with_grok(base64_image) for base64_image in base64_images]
        logger.debug(f"Processed images with Grok Vision Model. Results: {aggregated_results}")

        # Further processing with the Grok Text model
        response = process_document_with_text_model(aggregated_results)
        logger.debug(f"Processed document with Grok Text Model. Response: {response}")
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the document: {str(e)}")

@router.post("/generate-response", response_model=str)
def ask_question(request: QuestionRequest):
    try:
        logger.debug(f"Received request data: {request}")
        
        response = generate_response(request.dict())
        
        logger.debug(f"Generated response: {response}")
        return response 
        
    except Exception as e:
        logger.error(f"Error occurred while processing the request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")
