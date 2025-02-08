import logging
import os
import json
import re
from openai import OpenAI  
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
from api.db.queries import save_document_analysis
from api.db.database import SessionLocal

logger = logging.getLogger(__name__)

XAI_API_KEY = os.getenv("XAI_API_KEY")
VISION_MODEL_NAME = "grok-vision-beta"

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

class Position(BaseModel):
    x: float
    y: float
    width: float
    height: float

class Field(BaseModel):
    field_name: str
    position: Position
    required_value: str
    is_required: bool

class DocumentAnalysisResponse(BaseModel):
    fields: List[Field]

async def analyze_document_with_vision(base64_image: str, session_id: str) -> dict:
    """
    Analyzes a document from an image and extracts form fields, their exact location, and required data.

    :param base64_image: Document image in Base64 format.
    :return: A dictionary containing a list of detected fields with their names, locations, and required values.
    """
    try:
        logger.debug("Sending request to the Vision model...")
        
        # Send the request to OpenAI's API
        response = client.chat.completions.create(
            model=VISION_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low", 
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "Analyze this document and extract all form fields. "
                                "For each field, return the following information:\n"
                                "- 'field_name': The field name (e.g., 'Full Name').\n"
                                "- 'position': The exact location of the field in the document (e.g., X, Y coordinates, width, height).\n"
                                "- 'required_value': The type of data required in this field (e.g., 'Text', 'Number', 'Date', 'Email').\n"
                                "- 'is_required': Whether the field is mandatory (true/false).\n"
                                "Return the result in JSON format:\n"
                                "{\n"
                                "  \"fields\": [\n"
                                "    { \"field_name\": \"<field_label>\", \"position\": { \"x\": <x>, \"y\": <y>, \"width\": <width>, \"height\": <height> }, \"required_value\": \"<data_type>\", \"is_required\": <true/false> }\n"
                                "  ]\n"
                                "}"
                            )
                        }
                    ]
                }
            ]
        )
        
        logger.debug(f"Response received: {response}")
        
        # Accessing the 'choices' attribute correctly
        # response.choices is a list, we need to access the first element
        choice = response.choices[0]
        
        # If the message contains JSON data (fields in a structured format), we can process it here
        response_data = choice.message.content
        
        # Parsowanie odpowiedzi
        logger.debug(f"Raw response data (type: {type(response_data)}): {response_data}")
        
        if isinstance(response_data, str):
            try:
                # Usuń ewentualne znaki specjalne przed/po JSON
                json_str = re.sub(r'^[^{]*', '', response_data)  # Usuń wszystko przed {
                json_str = re.sub(r'[^}]*$', '', json_str)       # Usuń wszystko po }
                response_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Błąd parsowania JSON po oczyszczeniu: {e}")
                raise ValueError("Nieprawidłowy format odpowiedzi API")
        
        # Walidacja struktury
        if not isinstance(response_data, dict) or 'fields' not in response_data:
            logger.error(f"Nieprawidłowa struktura odpowiedzi: {response_data}")
            raise ValueError("Odpowiedź API nie zawiera wymaganej struktury")
            
        fields = []
        for field_data in response_data['fields']:
            try:
                # Dodaj walidację każdego pola
                if not all(key in field_data for key in ['field_name', 'position', 'required_value', 'is_required']):
                    logger.error(f"Niekompletne pole: {field_data}")
                    continue
                    
                # Walidacja pozycji
                position_data = field_data['position']
                if not all(k in position_data for k in ['x', 'y', 'width', 'height']):
                    logger.error(f"Nieprawidłowa pozycja: {position_data}")
                    continue
                    
                field = Field(
                    field_name=str(field_data["field_name"]),
                    position=Position(
                        x=float(position_data["x"]),
                        y=float(position_data["y"]),
                        width=float(position_data["width"]),
                        height=float(position_data["height"])
                    ),
                    required_value=str(field_data["required_value"]),
                    is_required=bool(field_data["is_required"])
                )
                fields.append(field)
            except (KeyError, ValueError, TypeError) as e:
                logger.error(f"Błąd przetwarzania pola: {e} | Dane: {field_data}")
                continue
                
        if not fields:
            raise ValueError("Brak wykrytych pól w dokumencie")
            
        # Zapisz wyniki do bazy
        async with SessionLocal() as session:
            await save_document_analysis(
                session=session,
                session_id=session_id,
                document_path=f"documents/{session_id}.pdf",
                fields=json.dumps(response_data['fields'])
            )
            
        return DocumentAnalysisResponse(fields=fields)
    
    except Exception as e:
        logger.error("Error processing image: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
