from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import logging

from core.database import get_db
from db.repositories import positions as positions_repo
from api.models.positions import Position, PositionCreate, PositionStats
from services.stock_service import StockService

router = APIRouter()
stock_service = StockService()

logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=List[Position],
    summary="Get all positions",
    description="Retrieve a list of all tracked stock positions in the portfolio.",
    response_description="List of stock positions"
)
def read_positions(
    skip: int = Query(0, description="Number of positions to skip"),
    limit: int = Query(100, description="Maximum number of positions to return"),
    db: Session = Depends(get_db)
):
    return positions_repo.get_positions(db, skip=skip, limit=limit)

@router.post(
    "/",
    response_model=Position,
    status_code=201,
    summary="Create new position",
    description="""
    Create a new stock position in the portfolio.
    
    - **symbol**: Stock ticker symbol (e.g., AAPL, MSFT)
    - **quantity**: Number of shares
    - **entry_price**: Price per share at entry
    """,
    response_description="Created position details"
)
def create_position(
    position: PositionCreate,
    db: Session = Depends(get_db)
):
    db_position = positions_repo.get_position(db, position.symbol)
    if db_position:
        raise HTTPException(
            status_code=400,
            detail=f"Position for {position.symbol} already exists"
        )
    return positions_repo.create_position(db, position)

@router.get(
    "/{symbol}",
    response_model=Position,
    summary="Get position by symbol",
    description="Retrieve details of a specific stock position by its symbol.",
    responses={
        404: {"description": "Position not found"},
        200: {
            "description": "Position details",
            "content": {
                "application/json": {
                    "example": {
                        "symbol": "AAPL",
                        "quantity": 100,
                        "entry_price": 150.00
                    }
                }
            }
        }
    }
)
def read_position(
    symbol: str,
    db: Session = Depends(get_db)
):
    position = positions_repo.get_position(db, symbol)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@router.get(
    "/{symbol}/stats",
    response_model=Dict,
    summary="Get position statistics",
    description="Get detailed statistics for a specific position",
    responses={
        404: {"description": "Position not found"},
        500: {"description": "Error fetching market data"}
    }
)
def get_position_stats(
    symbol: str,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Getting stats for symbol: {symbol}")
        position = positions_repo.get_position(db, symbol.upper())
        
        if not position:
            logger.warning(f"Position not found: {symbol}")
            raise HTTPException(status_code=404, detail="Position not found")
            
        logger.info(f"Found position: {position.symbol}")
        stats = stock_service.get_position_stats(position)
        
        logger.info(f"Successfully got stats for {symbol}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_position_stats: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing position: {str(e)}"
        )

@router.delete(
    "/{symbol}",
    status_code=204,
    summary="Delete position",
    description="Remove a stock position from the portfolio.",
    responses={
        204: {"description": "Position successfully deleted"},
        404: {"description": "Position not found"}
    }
)
def delete_position(
    symbol: str,
    db: Session = Depends(get_db)
):
    if not positions_repo.delete_position(db, symbol):
        raise HTTPException(status_code=404, detail="Position not found")
    return None 