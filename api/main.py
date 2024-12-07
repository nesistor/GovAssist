import os
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI as LangChainOpenAI

# FastAPI application initialization
app = FastAPI(title="Government Assistant API")

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["government_data"]

# OpenAI client initialization
XAI_API_KEY = os.getenv("XAI_API_KEY")
openai_client = OpenAI(api_key=XAI_API_KEY)

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
    """
    Adds a new ministry to the database.
    """
    ministry_dict = ministry.dict()
    result = db.ministries.insert_one(ministry_dict)
    return {"message": "Ministry added successfully.", "id": str(result.inserted_id)}

@app.post("/add-documents")
async def add_documents(documents: List[Document]):
    """
    Adds documents related to a ministry.
    """
    documents_list = [doc.dict() for doc in documents]
    result = db.documents.insert_many(documents_list)
    return {"message": "Documents added successfully.", "inserted_ids": [str(id) for id in result.inserted_ids]}

@app.post("/add-localization")
async def add_localization(localization: Localization):
    """
    Adds a location for a ministry.
    """
    localization_dict = localization.dict()
    result = db.localizations.insert_one(localization_dict)
    return {"message": "Localization added successfully.", "id": str(result.inserted_id)}

@app.post("/add-policy")
async def add_policy(policy: Policy):
    """
    Adds a policy related to a ministry.
    """
    policy_dict = policy.dict()
    result = db.policies.insert_one(policy_dict)
    return {"message": "Policy added successfully.", "id": str(result.inserted_id)}

# Helper function for generating responses
def generate_response_from_grok(context: str, question: str) -> str:
    """
    Generates a response using LangChain and Grok.
    """
    llm = LangChainOpenAI(openai_api_key=XAI_API_KEY)
    template = (
        "You are an expert in government policies. Here is the context:\n{context}\n"
        "Answer the following question based on this information:\n{question}"
    )
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({"context": context, "question": question})

@app.post("/generate-response")
async def generate_response(request: QuestionRequest):
    """
    Generates a response to the user's question based on ministry-related documents.
    The system automatically identifies the relevant ministry if not explicitly provided.
    """
    # Fetch all ministries and their associated data
    ministries = list(db.ministries.find())
    if not ministries:
        raise HTTPException(status_code=404, detail="No ministries found in the database.")

    # Retrieve all documents and group them by ministry
    all_documents = list(db.documents.find())
    ministry_contexts = {}
    for ministry in ministries:
        ministry_id = str(ministry["_id"])
        ministry_documents = [
            doc["content"] for doc in all_documents if doc["ministry_id"] == ministry_id
        ]
        if ministry_documents:
            ministry_contexts[ministry["name"]] = "\n".join(ministry_documents)

    if not ministry_contexts:
        raise HTTPException(status_code=404, detail="No documents found for any ministry.")

    # Generate Grok's understanding of the relevant ministry
    combined_context = "\n\n".join(
        f"Ministry: {name}\nDocuments:\n{context}"
        for name, context in ministry_contexts.items()
    )
    try:
        llm = LangChainOpenAI(openai_api_key=XAI_API_KEY)
        template = (
            "Below is a combined context of various ministries and their documents:\n{context}\n\n"
            "Question: {question}\n\n"
            "Identify the most relevant ministry and provide an answer to the question based on the documents."
        )
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        chain = LLMChain(llm=llm, prompt=prompt)

        # Run the chain to generate a response
        grok_response = chain.run({"context": combined_context, "question": request.question})

        return {"answer": grok_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# Test endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Government Assistant API!"}
