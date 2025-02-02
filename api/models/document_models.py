from pydantic import BaseModel
from typing import List

class DocumentCheckResult(BaseModel):
    is_valid: bool
    missing_fields: List[str]
    errors: List[str]

class QuestionRequest(BaseModel):
    user_id: str    
    question: str

class QuestionResponse(BaseModel):
    response: str

class DocumentRequest(BaseModel):
    document_type: str

class DocumentResponse(BaseModel):
    document_name: str
    url: str

class FunctionCallResultMessage(BaseModel):
    role: str
    content: str
    tool_call_id: str

class ConversationMessage(BaseModel):
    role: str
    content: str


