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

def has_ten_years_data(df):
    if df is None or df.empty:
        return False
    days_diff = (df.index.max() - df.index.min()).days
    return days_diff >= 3650  # ~10 Jahre

def main():
    df_constituents = pd.read_csv('../raw/sp500_constituents.csv')
    symbols = df_constituents['Symbol'].tolist()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=11*365)  # 11 Jahre für Puffer
    
    conn = create_database()
    cursor = conn.cursor()
    
    complete_symbols = []
    
    for symbol in symbols:
        print(f"Checking {symbol}")
        yahoo_symbol = symbol.replace('.','-')
        df = fetch_stock_data(yahoo_symbol, start_date, end_date)
        
        if has_ten_years_data(df):
            complete_symbols.append(symbol)
            print(f"✓ {symbol} has 10+ years data")
        else:
            print(f"✗ {symbol} insufficient history")
    
    print(f"\nFound {len(complete_symbols)} symbols with 10+ years history")
    
    for symbol in complete_symbols:
        print(f"Processing {symbol}")
        yahoo_symbol = symbol.replace('.','-')
        df = fetch_stock_data(yahoo_symbol, start_date, end_date)
        
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
        print(f"Stored data for {symbol}")
    
    print(f"\nStored data for all {len(complete_symbols)} complete symbols")
    conn.close()

if __name__ == "__main__":
    main()