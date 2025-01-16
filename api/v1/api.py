from fastapi import APIRouter
from api.v1.endpoints import positions

# Main API router that combines all endpoint routers
api_router = APIRouter()

# Add the positions endpoints under /positions path with "positions" tag
api_router.include_router(
    positions.router,
    prefix="/positions",
    tags=["positions"]
) 