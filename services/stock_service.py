from typing import List, Dict, Optional
import yfinance as yf
from datetime import datetime, timedelta
from fastapi import HTTPException
from db.models.positions import Position
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockService:
    def get_position_stats(self, position: Position) -> Dict:
        """Get stats for a single position"""
        logger.info(f"Getting stats for position: {position.symbol}")
        try:
            ticker = yf.Ticker(position.symbol)
            today = datetime.now().date()
            
            # Get market data including yesterday
            market_data = ticker.history(
                start=today - timedelta(days=2),
                end=today + timedelta(days=1),
                interval='1d'
            )
            
            if market_data.empty:
                logger.error(f"No market data available for {position.symbol}")
                raise ValueError(f"No market data available for {position.symbol}")

            # Get latest price (most recent close)
            current_price = float(market_data['Close'].iloc[-1])
            
            # Calculate basic stats
            total_cost = position.quantity * position.entry_price
            current_value = position.quantity * current_price
            total_pl = current_value - total_cost
            total_pl_pct = ((current_price - position.entry_price) / position.entry_price) * 100

            # Get yesterday's data if available
            if len(market_data) >= 2:
                yesterday_data = market_data.iloc[-2]
                today_data = market_data.iloc[-1]
                
                yesterday_stats = {
                    'open': float(yesterday_data['Open']),
                    'close': float(yesterday_data['Close']),
                    'high': float(yesterday_data['High']),
                    'low': float(yesterday_data['Low']),
                    'volume': int(yesterday_data['Volume'])
                }
                
                today_stats = {
                    'open': float(today_data['Open']),
                    'high': float(today_data['High']),
                    'low': float(today_data['Low']),
                    'volume': int(today_data['Volume'])
                }
            else:
                yesterday_stats = {
                    'open': 0, 'close': 0, 'high': 0, 'low': 0, 'volume': 0
                }
                today_stats = {
                    'open': 0, 'high': 0, 'low': 0, 'volume': 0
                }

            return {
                'symbol': position.symbol,
                'quantity': position.quantity,
                'entry_price': position.entry_price,
                'current_price': current_price,
                'total_cost': total_cost,
                'current_value': current_value,
                'total_pl': total_pl,
                'total_pl_pct': total_pl_pct,
                'yesterday': yesterday_stats,
                'today': today_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for {position.symbol}: {str(e)}")
            logger.exception("Full traceback:")
            raise ValueError(f"Error fetching data for {position.symbol}: {str(e)}") 