import pandas as pd
import sqlite3

def convert_sqlite_to_parquet():
    # Connect to SQLite database
    conn = sqlite3.connect('sp500_stock_data.db')
    
    # Read the entire table into a pandas DataFrame
    print("Reading data from SQLite database...")
    df = pd.read_sql_query("SELECT * FROM daily_prices", conn)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort data by symbol and date
    df = df.sort_values(['symbol', 'date'])
    
    # Write to Parquet file
    print("Converting to Parquet format...")
    df.to_parquet('sp500_stock_data.parquet', index=False)
    
    print("Conversion completed!")
    print(f"Total records converted: {len(df)}")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    convert_sqlite_to_parquet()
