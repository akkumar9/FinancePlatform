from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/financial_assistant")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(String, primary_key=True, index=True)
    employee_name = Column(String)
    employer = Column(String)
    urgency = Column(String)
    categories = Column(JSON)
    last_contact = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    financial_snapshot = Column(JSON)
    open_actions = Column(JSON)
    sentiment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.id"))
    sender = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ai_analysis = Column(JSON, nullable=True)
    
    case = relationship("Case", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.id"))
    filename = Column(String)
    file_path = Column(String)
    file_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    extracted_text = Column(Text, nullable=True)
    
    case = relationship("Case", back_populates="documents")

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    category = Column(String)
    eligibility_criteria = Column(Text)
    max_amount = Column(Integer, nullable=True)
    typical_approval_time = Column(String)
    application_difficulty = Column(String)
    success_rate = Column(Float)
    contact_info = Column(String)
    location = Column(String, nullable=True)

class CaseOutcome(Base):
    __tablename__ = "case_outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.id"))
    resolution = Column(String)
    resources_used = Column(JSON)
    success = Column(Boolean)
    credit_score_change = Column(Integer, nullable=True)
    money_saved = Column(Integer, nullable=True)
    resolved_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
