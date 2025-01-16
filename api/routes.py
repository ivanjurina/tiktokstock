from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from db import crud
from api import models
from services.stock_service import StockService

router = APIRouter()
stock_service = StockService()

@router.get("/positions/", response_model=List[models.Position])
def read_positions(db: Session = Depends(get_db)):
    return crud.get_positions(db)

@router.post("/positions/", response_model=models.Position)
def create_position(position: models.PositionCreate, db: Session = Depends(get_db)):
    db_position = crud.get_position(db, position.symbol)
    if db_position:
        raise HTTPException(status_code=400, detail="Position already exists")
    return crud.create_position(db, position)

@router.delete("/positions/{symbol}")
def delete_position(symbol: str, db: Session = Depends(get_db)):
    if crud.delete_position(db, symbol):
        return {"message": f"Position {symbol} deleted"}
    raise HTTPException(status_code=404, detail="Position not found")

@router.get("/positions/stats")
def get_positions_stats(db: Session = Depends(get_db)):
    positions = crud.get_positions(db)
    return stock_service.get_positions_stats(positions) 