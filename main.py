import yfinance as yf
import argparse
from datetime import datetime
import pytz

def get_stock_info(ticker_symbol):
    """
    Fetch stock information for the given ticker symbol
    """
    try:
        # Create ticker object
        ticker = yf.Ticker(ticker_symbol)
        
        # Get stock info
        info = ticker.info
        
        # Get today's data
        today_data = ticker.history(period='1d')
        
        if today_data.empty:
            return None
            
        # Calculate today's gains
        open_price = today_data['Open'][0]
        current_price = today_data['Close'][0]
        price_change = current_price - open_price
        price_change_percent = (price_change / open_price) * 100
        
        return {
            'name': info.get('longName', 'N/A'),
            'symbol': ticker_symbol,
            'current_price': current_price,
            'open_price': open_price,
            'price_change': price_change,
            'price_change_percent': price_change_percent,
            'volume': today_data['Volume'][0],
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A')
        }
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {str(e)}")
        return None

def format_number(number):
    """
    Format large numbers with commas and round floats to 2 decimal places
    """
    if isinstance(number, (int, float)):
        if isinstance(number, float):
            return f"{number:,.2f}"
        return f"{number:,}"
    return number

def display_stock_info(stock_data):
    """
    Display formatted stock information
    """
    if stock_data is None:
        print("No data available for the specified stock.")
        return
        
    print("\n=== Stock Information ===")
    print(f"Name: {stock_data['name']}")
    print(f"Symbol: {stock_data['symbol']}")
    print(f"Current Price: ${format_number(stock_data['current_price'])}")
    print(f"Open Price: ${format_number(stock_data['open_price'])}")
    
    # Format price change with color indicators (+ or -)
    price_change = stock_data['price_change']
    price_change_str = f"{'+' if price_change >= 0 else ''}{format_number(price_change)}"
    percent_change = stock_data['price_change_percent']
    percent_change_str = f"{'+' if percent_change >= 0 else ''}{format_number(percent_change)}%"
    
    print(f"Today's Change: ${price_change_str} ({percent_change_str})")
    print(f"Volume: {format_number(stock_data['volume'])}")
    print(f"Market Cap: ${format_number(stock_data['market_cap'])}")
    print(f"P/E Ratio: {format_number(stock_data['pe_ratio'])}")
    print(f"52 Week High: ${format_number(stock_data['fifty_two_week_high'])}")
    print(f"52 Week Low: ${format_number(stock_data['fifty_two_week_low'])}")
    print("=====================")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Get stock information for a given ticker symbol')
    parser.add_argument('ticker', type=str, help='Stock ticker symbol (e.g., AAPL)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get and display stock information
    stock_data = get_stock_info(args.ticker.upper())
    display_stock_info(stock_data)

if __name__ == "__main__":
    main()