from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
import json

Base = declarative_base()

class ConversationMessage(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"
    
    session_id = Column(String, primary_key=True)
    document_path = Column(String)
    fields = Column(Text)  # JSON jako string

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(String, primary_key=True)
    personal_data = Column(JSON)  # Przechowuje dane typu: {"full_name": "Jan Kowalski", "address": "...", ...}
