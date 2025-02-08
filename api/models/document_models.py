from pydantic import BaseModel
from typing import List

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
