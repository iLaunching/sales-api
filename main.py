"""
Minimal Sales API - With PostgreSQL + Redis + AI
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from database import init_db, close_db, get_db
from models import Conversation
from redis_client import close_redis, cache_conversation, get_cached_conversation, invalidate_cache
from llm_client import get_sales_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Sales API...")
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database init failed: {e}. Running without DB.")
    yield
    logger.info("Shutting down...")
    await close_db()
    close_redis()


app = FastAPI(
    title="Sales API - PostgreSQL + Redis + AI",
    version="1.3.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Sales API",
        "version": "1.3.0",
        "status": "running",
        "features": ["PostgreSQL", "Redis", "AI", "Conversations", "Caching"]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/sales/conversations")
async def create_conversation(data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new sales conversation"""
    try:
        conversation = Conversation(
            session_id=data.get("session_id", f"session-{datetime.now().timestamp()}"),
            email=data.get("email"),
            name=data.get("name"),
            company=data.get("company"),
            messages=[]
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        return {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "email": conversation.email,
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/conversations/{session_id}")
async def get_conversation(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get conversation by session ID - with Redis caching"""
    try:
        # Try cache first
        cached = get_cached_conversation(session_id)
        if cached:
            logger.info(f"Returning cached conversation for {session_id}")
            return cached
        
        # Cache miss - get from database
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        response = {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "email": conversation.email,
            "name": conversation.name,
            "company": conversation.company,
            "messages": conversation.messages,
            "current_stage": conversation.current_stage,
            "qualification_score": conversation.qualification_score,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None
        }
        
        # Cache for 30 minutes
        cache_conversation(session_id, response, ttl=1800)
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sales/message")
async def send_message(data: dict, db: AsyncSession = Depends(get_db)):
    """Send message and save to database"""
    try:
        session_id = data.get("session_id", "default")
        message_text = data.get("message", "")
        
        # Get or create conversation
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            conversation = Conversation(
                session_id=session_id,
                email=data.get("email"),
                messages=[]
            )
            db.add(conversation)
        
        # Add message to conversation
        messages = conversation.messages or []
        messages.append({
            "role": "user",
            "content": message_text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get AI response from LLM Gateway
        response_text = await get_sales_response(
            conversation_history=messages,
            user_message=message_text,
            context={
                "email": conversation.email,
                "name": conversation.name,
                "company": conversation.company,
                "stage": conversation.current_stage
            }
        )
        
        messages.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        conversation.messages = messages
        conversation.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(conversation)
        
        # Invalidate cache since conversation updated
        invalidate_cache(session_id)
        
        return {
            "message": response_text,
            "session_id": session_id,
            "conversation_id": conversation.id,
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
