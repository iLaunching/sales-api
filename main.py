"""
Sales API - AI-Powered Personalized Sales Conversations
Main FastAPI application for lead qualification and discovery
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routes.sales_routes import router as sales_router
from database.connection import init_db, close_db
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for database connections"""
    logger.info("Starting Sales API service...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}. Running without database.")
    yield
    logger.info("Shutting down Sales API service...")
    try:
        await close_db()
    except Exception as e:
        logger.warning(f"Database shutdown warning: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Sales API",
    description="AI-powered personalized sales conversations and lead qualification",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sales_router, prefix="/api/sales", tags=["sales"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Sales API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sales-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
