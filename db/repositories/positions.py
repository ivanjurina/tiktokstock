from sqlalchemy.orm import Session
from db.models.positions import Position
from api.models.positions import PositionCreate

def get_positions(db: Session, skip: int = 0, limit: int = 100):
    """Get all positions, returns empty list if none found"""
    return db.query(Position).offset(skip).limit(limit).all()

def get_position(db: Session, symbol: str):
    """Get single position, returns None if not found"""
    return db.query(Position).filter(Position.symbol == symbol).first()

def create_position(db: Session, position: PositionCreate):
    db_position = Position(**position.model_dump())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def delete_position(db: Session, symbol: str):
    position = db.query(Position).filter(Position.symbol == symbol).first()
    if position:
        db.delete(position)
        db.commit()
        return True
    return False

def clear_positions(db: Session):
    db.query(Position).delete()
    db.commit() 