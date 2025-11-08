"""
Sales API Routes
Handles all sales conversation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
import logging

from database.connection import get_db
from models.sales_conversation import (
    SalesConversation,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageRequest,
    MessageResponse,
)
from services.ai_sales_agent import AISalesAgent
from services.qualification_service import QualificationService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
sales_agent = AISalesAgent()
qualification_service = QualificationService()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new sales conversation"""
    try:
        new_conversation = SalesConversation(
            id=str(uuid.uuid4()),
            session_id=conversation.session_id,
            email=conversation.email,
            current_stage="greeting"
        )
        
        db.add(new_conversation)
        await db.commit()
        await db.refresh(new_conversation)
        
        logger.info(f"Created conversation {new_conversation.id} for session {conversation.session_id}")
        return new_conversation
    
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get conversation by ID"""
    result = await db.execute(
        select(SalesConversation).where(SalesConversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.get("/conversations/session/{session_id}", response_model=ConversationResponse)
async def get_conversation_by_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get conversation by session ID"""
    result = await db.execute(
        select(SalesConversation).where(SalesConversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message in the sales conversation
    Returns AI response with qualification updates
    """
    try:
        # Get or create conversation
        result = await db.execute(
            select(SalesConversation).where(SalesConversation.session_id == request.session_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            # Create new conversation
            conversation = SalesConversation(
                id=str(uuid.uuid4()),
                session_id=request.session_id,
                email=request.email,
                current_stage="greeting"
            )
            db.add(conversation)
        
        # Add user message to history
        conversation.messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": str(conversation.updated_at)
        })
        conversation.total_messages += 1
        
        # Generate AI response using sales agent
        ai_response = await sales_agent.generate_response(
            conversation=conversation,
            user_message=request.message
        )
        
        # Add AI message to history
        conversation.messages.append({
            "role": "assistant",
            "content": ai_response["message"],
            "timestamp": str(conversation.updated_at)
        })
        conversation.total_messages += 1
        
        # Update conversation stage
        conversation.current_stage = ai_response.get("stage", conversation.current_stage)
        
        # Update qualification if discovery data was extracted
        if ai_response.get("extracted_data"):
            extracted = ai_response["extracted_data"]
            
            # Update conversation fields
            if extracted.get("pain_points"):
                conversation.pain_points.extend(extracted["pain_points"])
            if extracted.get("goals"):
                conversation.goals.extend(extracted["goals"])
            if extracted.get("budget_signals"):
                conversation.budget_signals.extend(extracted["budget_signals"])
            if extracted.get("industry"):
                conversation.industry = extracted["industry"]
            if extracted.get("company_size"):
                conversation.company_size = extracted["company_size"]
            if extracted.get("urgency_level"):
                conversation.urgency_level = extracted["urgency_level"]
            if extracted.get("decision_authority"):
                conversation.decision_authority = extracted["decision_authority"]
            
            # Recalculate qualification score
            qualification = qualification_service.calculate_score(conversation)
            conversation.qualification_score = qualification["score"]
            conversation.quality_tier = qualification["tier"]
        
        # Update engagement score
        conversation.engagement_score = qualification_service.calculate_engagement(conversation)
        
        # Check if should handoff to auth
        should_handoff = (
            conversation.qualification_score >= 60 and
            conversation.current_stage == "qualification" and
            conversation.email is not None
        )
        
        sales_profile_id = None
        if should_handoff:
            sales_profile_id = str(uuid.uuid4())
            conversation.sales_profile_id = sales_profile_id
            conversation.converted = True
        
        await db.commit()
        await db.refresh(conversation)
        
        return MessageResponse(
            message=ai_response["message"],
            stage=conversation.current_stage,
            qualification_score=conversation.qualification_score,
            should_handoff=should_handoff,
            sales_profile_id=sales_profile_id
        )
    
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time sales conversation
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for session {session_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message")
            
            if not message:
                await websocket.send_json({"error": "Message is required"})
                continue
            
            # TODO: Process message through sales agent
            # TODO: Send streaming response back
            
            await websocket.send_json({
                "message": "WebSocket response (to be implemented)",
                "stage": "discovery"
            })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@router.get("/analytics/summary")
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """Get sales analytics summary"""
    # TODO: Implement analytics aggregation
    return {
        "total_conversations": 0,
        "conversion_rate": 0.0,
        "average_qualification_score": 0.0,
        "high_quality_leads": 0
    }
