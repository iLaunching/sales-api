"""
Database models for Sales API
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Conversation(Base):
    """Sales conversation tracking"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), index=True)
    name = Column(String(255))
    company = Column(String(255))
    
    # Conversation data
    messages = Column(JSON, default=list)  # List of {role, content, timestamp}
    current_stage = Column(String(50), default="greeting")  # greeting, discovery, qualification, pitch, handoff
    
    # Discovery data
    pain_points = Column(JSON, default=list)
    goals = Column(JSON, default=list)
    industry = Column(String(255))
    company_size = Column(String(50))
    role = Column(String(255))
    
    # Qualification
    qualification_score = Column(Float, default=0.0)
    quality_tier = Column(String(20))  # high, medium, low
    
    # Status
    converted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Conversation {self.session_id} - {self.email}>"
