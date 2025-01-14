import pandas as pd
import yfinance as yf
import sqlite3
from datetime import datetime, timedelta
import time

def create_database():
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
    try:
        time.sleep(1)
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def is_complete_data(df, min_days_per_year=240):
    if df is None or df.empty:
        return False
        
    years = (df.index.max() - df.index.min()).days / 365
    required_days = int(years * min_days_per_year)
    actual_days = len(df)
    
    return actual_days >= required_days

def main():
    df_constituents = pd.read_csv('../raw/sp500_constituents.csv')
    symbols = df_constituents['Symbol'].tolist()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=11*365)
    
    conn = create_database()
    cursor = conn.cursor()
    
    total_symbols = len(symbols)
    complete_count = 0
    incomplete_count = 0
    
    for idx, symbol in enumerate(symbols, 1):
        print(f"Processing {symbol} ({idx}/{total_symbols})")
        yahoo_symbol = symbol.replace('.','-')
        
        df = fetch_stock_data(yahoo_symbol, start_date, end_date)
        
        if is_complete_data(df):
            complete_count += 1
            for index, row in df.iterrows():
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
            conn.commit()
            print(f"Stored complete data for {symbol}")
        else:
            incomplete_count += 1
            print(f"Skipped {symbol} - incomplete data")
    
    print(f"\nProcessing completed:")
    print(f"Complete symbols: {complete_count}")
    print(f"Incomplete symbols: {incomplete_count}")
    conn.close()

if __name__ == "__main__":
    main()