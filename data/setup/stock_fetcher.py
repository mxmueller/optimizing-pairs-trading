import pandas as pd
import yfinance as yf
import sqlite3
from datetime import datetime, timedelta
import time

def create_database():
    """Create SQLite database and required table"""
    conn = sqlite3.connect('sp500_stock_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_prices (
            symbol TEXT,
            date DATE,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    ''')
    
    conn.commit()
    return conn

def fetch_stock_data(symbol, start_date, end_date):
    """Fetch stock data for a given symbol and date range"""
    try:
        # Add delay to prevent rate limiting
        time.sleep(1)
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def main():
    # Read S&P 500 constituents
    df_constituents = pd.read_csv('constituents.csv')
    symbols = df_constituents['Symbol'].tolist()
    
    # Calculate date range (5 years from today)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    # Create database connection
    conn = create_database()
    cursor = conn.cursor()
    
    total_symbols = len(symbols)
    print(f"Starting data collection for {total_symbols} symbols...")
    
    # Process each symbol
    for idx, symbol in enumerate(symbols, 1):
        print(f"Processing {symbol} ({idx}/{total_symbols})")
        
        # Handle special cases where symbol contains dots
        yahoo_symbol = symbol.replace('.','-')
        
        df = fetch_stock_data(yahoo_symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            # Prepare data for database
            for index, row in df.iterrows():
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO daily_prices 
                        (symbol, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol,
                        index.strftime('%Y-%m-%d'),
                        row['Open'],
                        row['High'],
                        row['Low'],
                        row['Close'],
                        row['Volume']
                    ))
                except Exception as e:
                    print(f"Error inserting data for {symbol} on {index}: {str(e)}")
            
            conn.commit()
            print(f"Successfully stored data for {symbol}")
        else:
            print(f"No data available for {symbol}")
    
    conn.close()
    print("\nData collection completed!")
    print("Data has been stored in 'sp500_stock_data.db'")

if __name__ == "__main__":
    main()
