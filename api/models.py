from pydantic import BaseModel

class PositionBase(BaseModel):
    symbol: str
    quantity: float
    entry_price: float

class PositionCreate(PositionBase):
    pass

class Position(PositionBase):
    class Config:
        from_attributes = True

class StockData(BaseModel):
    symbol: str
    current_price: float
    yesterday_open: float
    yesterday_close: float
    yesterday_change: float
    yesterday_change_pct: float
    today_open: float
    today_change: float
    today_change_pct: float 