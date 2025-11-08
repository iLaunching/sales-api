"""
Sales conversation data models
Tracks all sales discovery conversations, user profiles, and qualification scores
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

from database.connection import Base


class SalesConversation(Base):
    """SQLAlchemy model for sales conversations"""
    __tablename__ = "sales_conversations"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    
    # User Information
    email = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    role = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    
    # Conversation Data
    messages = Column(JSON, default=list)  # List of {role, content, timestamp}
    current_stage = Column(String, default="greeting")  # greeting, discovery, qualification, handoff
    
    # Discovery Insights
    pain_points = Column(JSON, default=list)
    goals = Column(JSON, default=list)
    budget_signals = Column(JSON, default=list)
    urgency_level = Column(String, nullable=True)  # low, medium, high
    decision_authority = Column(String, nullable=True)  # decision_maker, influencer, researcher
    
    # Qualification
    qualification_score = Column(Float, default=0.0)  # 0-100
    quality_tier = Column(String, nullable=True)  # high, medium, low
    
    # Engagement Metrics
    engagement_score = Column(Float, default=0.0)
    total_messages = Column(Integer, default=0)
    conversation_duration = Column(Integer, default=0)  # seconds
    drop_off_stage = Column(String, nullable=True)
    
    # Personalization
    pitch_variant = Column(String, nullable=True)  # For A/B testing
    features_matched = Column(JSON, default=list)
    success_stories_shown = Column(JSON, default=list)
    
    # Conversion
    converted = Column(Boolean, default=False)
    sales_profile_id = Column(String, nullable=True)  # ID sent to auth API
    handoff_timestamp = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional context
    context_data = Column(JSON, default=dict)  # Flexible storage for any additional data


# Pydantic schemas for API
class ConversationMessage(BaseModel):
    """Single conversation message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime


class ConversationCreate(BaseModel):
    """Create new conversation"""
    session_id: str
    email: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Update conversation data"""
    email: Optional[str] = None
    name: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    role: Optional[str] = None
    company_size: Optional[str] = None
    current_stage: Optional[str] = None
    pain_points: Optional[list] = None
    goals: Optional[list] = None
    budget_signals: Optional[list] = None
    urgency_level: Optional[str] = None
    decision_authority: Optional[str] = None
    qualification_score: Optional[float] = None
    quality_tier: Optional[str] = None
    engagement_score: Optional[float] = None
    context_data: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: str
    session_id: str
    email: Optional[str]
    name: Optional[str]
    company: Optional[str]
    current_stage: str
    qualification_score: float
    quality_tier: Optional[str]
    engagement_score: float
    converted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    """Request to send a message"""
    session_id: str
    message: str
    email: Optional[str] = None


class MessageResponse(BaseModel):
    """Response from sales conversation"""
    message: str
    stage: str
    qualification_score: Optional[float] = None
    should_handoff: bool = False
    sales_profile_id: Optional[str] = None
