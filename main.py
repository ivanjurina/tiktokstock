from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from core.database import engine
from db.models.positions import Position
from api.v1.api import api_router
from core.config import settings

# Create database tables
Position.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stock Portfolio Tracker",
    description="""
    A comprehensive API for tracking stock positions and market data.
    
    Features:
    * Track stock positions with entry prices and quantities
    * Real-time market data integration
    * Historical price analysis
    * Portfolio performance metrics
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)