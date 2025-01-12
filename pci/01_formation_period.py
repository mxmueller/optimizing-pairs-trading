from clickhouse_driver import Client
from datetime import datetime, timedelta

def get_formation_periods():
    client = Client(host='localhost', port=9000, user='default', password='password')
    
    client.execute('DROP TABLE IF EXISTS formation_periods')
    client.execute('''
    CREATE TABLE IF NOT EXISTS formation_periods
    (
        pair_key String,
        period_start Date,
        period_end Date,
        formation_end Date,
        symbol1 String,
        symbol2 String
    ) ENGINE = MergeTree()
    ORDER BY (pair_key, period_start)
    ''')

    client.execute('DROP TABLE IF EXISTS formation_prices')
    client.execute('''
    CREATE TABLE IF NOT EXISTS formation_prices
    (
        pair_key String,
        period_start Date,
        date Date,
        price1 Float64,
        price2 Float64
    ) ENGINE = MergeTree()
    ORDER BY (pair_key, period_start, date)
    ''')

    pairs = client.execute('SELECT pair_key, symbol1, symbol2 FROM stock_pairs')
    
    start_date = client.execute('SELECT min(date) FROM stock_data')[0][0]
    
    period_data = []
    for pair_key, sym1, sym2 in pairs:
        # 48 months formation period
        formation_end = client.execute(f'''
            SELECT dateAdd(MONTH, 48, toDate('{start_date}'))
        ''')[0][0]
        
        # 6 months trading period
        period_end = client.execute(f'''
            SELECT dateAdd(MONTH, 6, toDate('{formation_end}'))
        ''')[0][0]
        
        period_data.append((pair_key, start_date, period_end, formation_end, sym1, sym2))
    
    if period_data:
        client.execute('INSERT INTO formation_periods VALUES', period_data)
        
        client.execute('''
        INSERT INTO formation_prices
        SELECT 
            fp.pair_key,
            fp.period_start,
            p1.date,
            p1.close as price1,
            p2.close as price2
        FROM formation_periods fp
        JOIN stock_data p1 ON p1.symbol = fp.symbol1
        JOIN stock_data p2 ON p2.symbol = fp.symbol2 AND p1.date = p2.date
        WHERE p1.date BETWEEN fp.period_start AND fp.period_end
        ''')

if __name__ == "__main__":
    get_formation_periods()