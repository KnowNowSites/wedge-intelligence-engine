"""
Main FastAPI application for Wedge Intelligence Engine.
Initializes database, scrapers, detectors, and scheduler.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import init_database
from backend.config import Config, create_env_template
from backend.utils import get_logger

logger = get_logger("main")


# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting Wedge Intelligence Engine...")
    create_env_template()
    init_database()
    
    if Config.validate():
        logger.info("Configuration validated ✓")
    else:
        logger.warning("Configuration incomplete - some scrapers may be disabled")
    
    # Start scheduler if enabled
    if Config.SCHEDULER_ENABLED:
        logger.info("Scheduler enabled - starting background tasks...")
        # TODO: Initialize and start APScheduler
    
    yield
    
    # Shutdown
    logger.info("Shutting down Wedge Intelligence Engine...")
    # TODO: Gracefully stop scheduler


# Create FastAPI app
app = FastAPI(
    title="Wedge Intelligence Engine",
    description="Market research tool for identifying profitable business wedges",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Wedge Intelligence Engine",
        "version": "1.0.0",
    }


# TODO: Add API routes
# - GET /api/wedges - List all wedge profiles
# - GET /api/wedges/:id - Get single wedge detail
# - GET /api/signals - List all raw signals
# - GET /api/watchlist - Get user's watchlist
# - POST /api/watchlist/:wedge_id - Add to watchlist
# - etc.


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=Config.LOG_LEVEL.lower(),
    )
