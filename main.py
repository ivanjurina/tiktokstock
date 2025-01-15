import yfinance as yf
from datetime import datetime, timedelta
from tabulate import tabulate
from colorama import init, Fore, Style
import os
import sqlite3

# Initialize colorama
init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_premarket_movement(positions):
    results = []
    for symbol, position_data in positions.items():
        try:
            ticker = yf.Ticker(symbol)
            today = datetime.now().date()
            
            # Get today's regular market data
            today_data = ticker.history(
                start=today - timedelta(days=1),
                end=today + timedelta(days=1),
                interval='1d'
            )
            
            # Get pre-market data
            premarket_data = ticker.history(
                start=today,
                end=today + timedelta(days=1),
                interval='1m',
                prepost=True
            )
            premarket_data = premarket_data.between_time('04:00', '09:30')
            
            if len(today_data) > 0 and len(premarket_data) > 0:
                current_price = premarket_data['Close'].iloc[-1]
                entry_price = position_data['entry_price']
                quantity = position_data['quantity']
                
                # Get today's open and previous close
                prev_close = today_data['Close'].iloc[-2]
                today_open = today_data['Open'].iloc[-1]
                
                # Calculate position P/L
                total_value = quantity * current_price
                total_cost = quantity * entry_price
                position_pl = total_value - total_cost
                position_pl_pct = ((current_price - entry_price) / entry_price) * 100
                
                # Calculate today's movement
                today_change = current_price - prev_close
                today_change_pct = (today_change / prev_close) * 100
                
                # Format position P/L string
                pl_str = f"${position_pl:.2f} ({position_pl_pct:.2f}%)"
                if position_pl > 0:
                    pl_str = f"{Fore.GREEN}{pl_str}{Style.RESET_ALL}"
                elif position_pl < 0:
                    pl_str = f"{Fore.RED}{pl_str}{Style.RESET_ALL}"
                
                # Format today's change string
                today_change_str = f"${today_change:.2f} ({today_change_pct:.2f}%)"
                if today_change > 0:
                    today_change_str = f"{Fore.GREEN}{today_change_str}{Style.RESET_ALL}"
                elif today_change < 0:
                    today_change_str = f"{Fore.RED}{today_change_str}{Style.RESET_ALL}"
                
                results.append([
                    symbol,
                    f"{quantity:.2f}",
                    f"${entry_price:.2f}",
                    f"${prev_close:.2f}",
                    f"${today_open:.2f}",
                    f"${current_price:.2f}",
                    today_change_str,
                    pl_str,
                    f"${total_value:.2f}"
                ])
            else:
                results.append([
                    symbol,
                    f"{position_data['quantity']:.2f}", 
                    f"${position_data['entry_price']:.2f}",
                    "No data",
                    "No data",
                    "No data",
                    "No data",
                    "",
                    ""
                ])
        except Exception as e:
            results.append([
                symbol,
                f"{position_data['quantity']:.2f}", 
                f"${position_data['entry_price']:.2f}",
                "Error",
                "Error",
                f"Error: {str(e)}",
                "",
                "",
                ""
            ])
    
    return results

def display_results(results):
    clear_screen()
    if results:
        headers = ["Symbol", "Quantity", "Entry", "Prev Close", "Today Open", "Current", "Today's Move", "Total P/L", "Total Value"]
        print("\nPosition Summary:")
        print(tabulate(results, headers=headers, tablefmt="grid"))
    else:
        print("\nNo positions added yet!")

def init_database():
    """Initialize SQLite database and create table if it doesn't exist"""
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS positions
        (symbol TEXT PRIMARY KEY,
         quantity REAL NOT NULL,
         entry_price REAL NOT NULL)
    ''')
    conn.commit()
    conn.close()

def load_positions():
    """Load positions from database"""
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute('SELECT symbol, quantity, entry_price FROM positions')
    positions = {row[0]: {"quantity": row[1], "entry_price": row[2]} for row in c.fetchall()}
    conn.close()
    return positions

def save_position(symbol, quantity, entry_price):
    """Save a position to database"""
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR REPLACE INTO positions (symbol, quantity, entry_price) 
            VALUES (?, ?, ?)
        ''', (symbol, quantity, entry_price))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving position: {e}")
        return False
    finally:
        conn.close()

def remove_position(symbol):
    """Remove a position from database"""
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute('DELETE FROM positions WHERE symbol = ?', (symbol,))
    was_removed = c.rowcount > 0
    conn.commit()
    conn.close()
    return was_removed

def clear_positions():
    """Clear all positions from database"""
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute('DELETE FROM positions')
    conn.commit()
    conn.close()

def main():
    init_database()
    positions = load_positions()
    
    while True:
        print("\nStock Position Tracker")
        print("1. Add position")
        print("2. Remove position")
        print("3. Show current stats")
        print("4. Clear all positions")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            symbol = input("Enter ticker symbol: ").upper()
            try:
                quantity = float(input("Enter quantity: "))
                entry_price = float(input("Enter entry price: $"))
                if save_position(symbol, quantity, entry_price):
                    positions[symbol] = {"quantity": quantity, "entry_price": entry_price}
                    print(f"Added position: {symbol}")
                else:
                    print("Failed to add position!")
            except ValueError:
                print("Invalid quantity or price! Please enter numeric values.")
        
        elif choice == '2':
            if positions:
                symbol = input("Enter ticker symbol to remove: ").upper()
                if remove_position(symbol):
                    del positions[symbol]
                    print(f"Removed position: {symbol}")
                else:
                    print("Position not found!")
            else:
                print("No positions to remove!")
        
        elif choice == '3':
            if positions:
                results = get_premarket_movement(positions)
                display_results(results)
            else:
                print("No positions added yet!")
        
        elif choice == '4':
            clear_positions()
            positions.clear()
            print("All positions cleared!")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()