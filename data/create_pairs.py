from clickhouse_driver import Client
import pandas as pd
from itertools import combinations

def create_pairs():
    client = Client(host='localhost', port=9000, user='default', password='password')
    
    client.execute('''
    CREATE TABLE IF NOT EXISTS stock_pairs
    (
        pair_key String,
        sector String,
        symbol1 String,
        symbol2 String,
        sub_industry1 String,
        sub_industry2 String
    ) ENGINE = MergeTree()
    ORDER BY pair_key
    ''')

    sectors_data = client.execute('''
    SELECT 
        symbol,
        gics_sector as sector,
        gics_sub_industry as sub_industry
    FROM stock_constituents
    ORDER BY gics_sector, symbol
    ''')
    
    df = pd.DataFrame(sectors_data, columns=['symbol', 'sector', 'sub_industry'])
    pairs_data = []
    
    for sector in df['sector'].unique():
        sector_stocks = df[df['sector'] == sector]
        symbols = sector_stocks['symbol'].tolist()
        
        for sym1, sym2 in combinations(symbols, 2):
            stock1 = sector_stocks[sector_stocks['symbol'] == sym1].iloc[0]
            stock2 = sector_stocks[sector_stocks['symbol'] == sym2].iloc[0]
            sector_clean = sector.replace(' ', '_').upper()
            
            pairs_data.append((
                f"{sector_clean}_{sym1}_{sym2}",
                sector,
                sym1,
                sym2,
                stock1['sub_industry'],
                stock2['sub_industry']
            ))
    
    if pairs_data:
        client.execute('INSERT INTO stock_pairs VALUES', pairs_data)

if __name__ == "__main__":
    create_pairs()