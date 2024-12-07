import os
from fastapi import FastAPI, HTTPException, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from openai import OpenAI

# Initialize FastAPI application
app = FastAPI(title="GovGiggler - Smart Government Assistant", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# Storage for documents and appointments
documents = []
appointments = []

# Data Models
class AskRequest(BaseModel):
    question: str

class Appointment(BaseModel):
    name: str
    service: str
    date: datetime

class DocumentRequirementsRequest(BaseModel):
    service: str

class Feedback(BaseModel):
    user: str
    feedback: str
    rating: int = Field(..., ge=1, le=5)

class MinistryLocationRequest(BaseModel):
    ministry: str

# Endpoint for uploading documents
@app.post("/upload")
async def upload_document(file: UploadFile):
    """
    Endpoint for uploading documents.
    Supports plain text and PDF formats.
    """
    if file.content_type not in ["text/plain", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Only plain text and PDF files are supported.")

    content = await file.read()
    documents.append({"filename": file.filename, "content": content.decode("utf-8")})
    return {"message": "Document uploaded successfully.", "filename": file.filename}

# Endpoint for asking questions
@app.post("/ask")
async def ask_question(request: AskRequest):
    """
    Endpoint for asking questions.
    Uses previously uploaded documents for context.
    """
    if not documents:
        raise HTTPException(status_code=400, detail="No documents uploaded. Please upload documents first.")

    # Combine all uploaded documents into a single context
    context = "\n".join(doc["content"] for doc in documents)

    # Send the question to the Grok AI model
    try:
        completion = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
                {"role": "user", "content": f"Context: {context}"},
                {"role": "user", "content": request.question},
            ],
        )
        response = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with the AI: {str(e)}")

    return {"answer": response}

# Endpoint for retrieving document requirements
@app.post("/document-requirements")
async def get_document_requirements(request: DocumentRequirementsRequest):
    """
    Endpoint for retrieving document requirements for a specific service.
    """
    # Mock document requirements
    mock_requirements = {
        "passport renewal": ["Application form", "Old passport", "Two passport-sized photos"],
        "driver's license renewal": ["ID card", "Old driver's license", "Medical certificate"],
    }

    requirements = mock_requirements.get(request.service.lower())
    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found for the specified service.")

    return {"service": request.service, "requirements": requirements}

# Endpoint for scheduling an appointment
@app.post("/schedule-appointment")
async def schedule_appointment(appointment: Appointment):
    """
    Endpoint for scheduling an appointment.
    """
    if appointment.date < datetime.now():
        raise HTTPException(status_code=400, detail="Appointment date must be in the future.")

    appointments.append(appointment)
    return {"message": "Appointment scheduled successfully.", "appointment": appointment}

# Endpoint for submitting feedback
@app.post("/feedback")
async def submit_feedback(feedback: Feedback):
    """
    Endpoint for submitting user feedback.
    """
    # Feedback can be logged or saved in a database
    return {"message": "Feedback submitted successfully.", "feedback": feedback}

# Endpoint for retrieving ministry locations
@app.post("/ministry-location")
async def get_ministry_location(request: MinistryLocationRequest):
    """
    Endpoint for retrieving the location of a specified ministry.
    """
    # Mock ministry locations
    mock_locations = {
        "ministry of health": "123 Wellness Street, Capital City",
        "ministry of transport": "456 Mobility Avenue, Capital City",
    }

    location = mock_locations.get(request.ministry.lower())
    if not location:
        raise HTTPException(status_code=404, detail="No location found for the specified ministry.")

    return {"ministry": request.ministry, "location": location}

# Test endpoint
@app.get("/")
def read_root():
    """
    Test endpoint for the application.
    """
    return {
        "message": "Welcome to GovGiggler - Your Smart Government Assistant!",
        "docs_url": "/docs",
    }
