from clickhouse_driver import Client
import numpy as np
from tqdm import tqdm

def calculate_sharpe_for_pair(client, pair_key, formation_end):
    # Get Kalman filter formation period statistics
    formation_stats = client.execute(f'''
        SELECT 
            avg(mt) as mean_mt,
            stddevPop(mt) as std_mt
        FROM kalman_results
        WHERE pair_key = '{pair_key}'
        AND date <= '{formation_end}'
    ''')
    
    if not formation_stats or not formation_stats[0][0] or not formation_stats[0][1]:
        return 0.0
        
    mean_mt, std_mt = formation_stats[0]
    
    # Get trading data for formation period
    trading_data = client.execute(f'''
        SELECT k.date, k.mt, p.price1, p.price2, pr.beta
        FROM kalman_results k
        JOIN formation_prices p ON k.pair_key = p.pair_key AND k.date = p.date
        JOIN pci_results pr ON k.pair_key = pr.pair_key
        WHERE k.pair_key = '{pair_key}'
        AND k.date <= '{formation_end}'
        ORDER BY k.date
    ''')
    
    if not trading_data:
        return 0.0
        
    position = 0
    returns = []
    entry_price1 = entry_price2 = None
    
    for i in range(1, len(trading_data)):
        date, mt, price1, price2, beta = trading_data[i]
        prev_date, _, prev_price1, prev_price2, _ = trading_data[i-1]
        
        z_score = (mt - mean_mt) / std_mt
        hedge_ratio = beta * price1 / price2
        
        # Position logic
        prev_position = position
        if position == 0:
            if z_score > 1.0:
                position = -1
                entry_price1, entry_price2 = price1, price2
            elif z_score < -1.0:
                position = 1
                entry_price1, entry_price2 = price1, price2
        else:
            if (position > 0 and z_score > -0.5) or (position < 0 and z_score < 0.5):
                position = 0
        
        # Calculate returns on position changes
        if position != prev_position and prev_position != 0:
            price_ratio1 = price1/prev_price1
            price_ratio2 = price2/prev_price2
            ret = prev_position * (price_ratio1 - hedge_ratio * price_ratio2)
            returns.append(ret)
    
    if not returns or len(returns) < 2:
        return 0.0
        
    returns = np.array(returns)
    return np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0

def update_sharpe_ratios():
    client = Client(host='localhost', port=9000, user='default', password='password')
    
    # Get all pairs that need Sharpe ratios
    pairs = client.execute('''
        SELECT DISTINCT p.pair_key, p.formation_end
        FROM formation_periods p
        JOIN pci_results pr ON p.pair_key = pr.pair_key
    ''')
    
    print(f"Calculating Sharpe ratios for {len(pairs)} pairs...")
    
    for pair_key, formation_end in tqdm(pairs):
        sharpe = calculate_sharpe_for_pair(client, pair_key, formation_end)
        
        # Update the PCI results with the calculated Sharpe ratio
        client.execute(f'''
            ALTER TABLE pci_results
            UPDATE in_sample_sharpe = {sharpe}
            WHERE pair_key = '{pair_key}'
        ''')
    
    print("Done!")

if __name__ == "__main__":
    update_sharpe_ratios()
