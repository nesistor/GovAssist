import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from openai import OpenAI

# FastAPI application initialization
app = FastAPI(title="Government Assistant API")

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["government_data"]

# OpenAI client initialization
XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# Data models
class Ministry(BaseModel):
    name: str
    description: Optional[str] = None

class Document(BaseModel):
    ministry_id: str
    title: str
    content: str

class Localization(BaseModel):
    ministry_id: str
    address: str
    city: str
    contact: Optional[str] = None

class Policy(BaseModel):
    ministry_id: str
    title: str
    description: str

class QuestionRequest(BaseModel):
    question: str
    ministry_name: Optional[str] = None

# CRUD endpoints
@app.post("/add-ministry")
async def add_ministry(ministry: Ministry):
    ministry_dict = ministry.dict()
    result = db.ministries.insert_one(ministry_dict)
    return {"message": "Ministry added successfully.", "id": str(result.inserted_id)}

@app.post("/add-documents")
async def add_documents(documents: List[Document]):
    documents_list = [doc.dict() for doc in documents]
    result = db.documents.insert_many(documents_list)
    return {"message": "Documents added successfully.", "inserted_ids": [str(id) for id in result.inserted_ids]}

@app.post("/add-localization")
async def add_localization(localization: Localization):
    localization_dict = localization.dict()
    result = db.localizations.insert_one(localization_dict)
    return {"message": "Localization added successfully.", "id": str(result.inserted_id)}

@app.post("/add-policy")
async def add_policy(policy: Policy):
    policy_dict = policy.dict()
    result = db.policies.insert_one(policy_dict)
    return {"message": "Policy added successfully.", "id": str(result.inserted_id)}

# Helper function for generating responses with Grok 1.5
def generate_response_from_grok(context: str, question: str) -> str:
    """
    Generates a response using Grok 1.5.
    """
    template = (
        "You are an expert in government policies. Here is the context:\n{context}\n"
        "Answer the following question based on this information:\n{question}"
    )
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    chain = LLMChain(llm=LangChainOpenAI(openai_api_key=XAI_API_KEY), prompt=prompt)
    return chain.run({"context": context, "question": question})

# Function for Grok-based model selection
def call_grok_model(model_name: str, messages: List[dict]) -> str:
    """
    Calls the appropriate Grok model for a given task (generation or validation).
    """
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        return completion.choices[0].message['content']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with Grok model: {str(e)}")

@app.post("/generate-response")
async def generate_response(request: QuestionRequest):
    """
    Generates a response to the user's question based on ministry-related documents.
    """
    if request.ministry_name:
        ministry = db.ministries.find_one({"name": request.ministry_name})
        if not ministry:
            raise HTTPException(status_code=404, detail="Ministry not found.")
        documents = db.documents.find({"ministry_id": str(ministry["_id"])})
        context = "\n".join(doc["content"] for doc in documents)
        if not context:
            raise HTTPException(status_code=404, detail="No documents found for this ministry.")
        answer = generate_response_from_grok(context, request.question)
        return {"ministry_name": request.ministry_name, "answer": answer}

    else:
        ministries = list(db.ministries.find())
        if not ministries:
            raise HTTPException(status_code=404, detail="No ministries found.")
        all_documents = list(db.documents.find())
        ministry_contexts = {}
        for ministry in ministries:
            ministry_id = str(ministry["_id"])
            ministry_documents = [
                doc["content"] for doc in all_documents if doc["ministry_id"] == ministry_id
            ]
            if ministry_documents:
                ministry_contexts[ministry["name"]] = "\n".join(ministry_documents)
        combined_context = "\n\n".join(
            f"Ministry: {name}\nDocuments:\n{context}" 
            for name, context in ministry_contexts.items()
        )
        grok_response = call_grok_model(
            model_name="grok-beta", 
            messages=[
                {"role": "system", "content": "You are a government assistant."},
                {"role": "user", "content": request.question},
                {"role": "system", "content": f"Context:\n{combined_context}"}
            ]
        )
        return {"answer": grok_response}

# Endpoint for document validation (using Grok Vision Beta)
@app.post("/validate-document")
async def validate_document(file: UploadFile = File(...)):
    """
    Validates a user-submitted document using Grok 2.0 (Grok Vision Beta).
    """
    try:
        file_content = await file.read()
        document_content = file_content.decode("utf-8")
        validation_result = call_grok_model(
            model_name="grok-vision-beta", 
            messages=[
                {"role": "system", "content": "You are a document validation expert."},
                {"role": "user", "content": document_content}
            ]
        )
        return {"validation_result": validation_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

# Test endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Government Assistant API!"}
