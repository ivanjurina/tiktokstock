from sqlalchemy import Column, Float, String
from core.database import Base

class Position(Base):
    __tablename__ = "positions"

    symbol = Column(String, primary_key=True, index=True)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False) 