from abc import ABC, abstractmethod
import yfinance as yf
from datetime import datetime, timedelta

class MarketDataProvider(ABC):
    """Abstract base class for market data providers"""
    
    @abstractmethod
    async def get_market_data(self, symbol: str, days: int):
        pass

    @abstractmethod
    async def validate_symbol(self, symbol: str):
        pass

class YFinanceProvider(MarketDataProvider):
    """Concrete implementation using yfinance"""
    
    async def get_market_data(self, symbol: str, days: int):
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return ticker.history(
            start=start_date,
            end=end_date,
            interval='1d'
        )

    async def validate_symbol(self, symbol: str):
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            raise ValueError(f"Invalid symbol: {symbol}") 