from sqlalchemy.orm import Session
from . import models
from api.models import PositionCreate

def get_positions(db: Session):
    return db.query(models.Position).all()

def get_position(db: Session, symbol: str):
    return db.query(models.Position).filter(models.Position.symbol == symbol).first()

def create_position(db: Session, position: PositionCreate):
    db_position = models.Position(**position.model_dump())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def delete_position(db: Session, symbol: str):
    position = db.query(models.Position).filter(models.Position.symbol == symbol).first()
    if position:
        db.delete(position)
        db.commit()
        return True
    return False

def clear_positions(db: Session):
    db.query(models.Position).delete()
    db.commit() 