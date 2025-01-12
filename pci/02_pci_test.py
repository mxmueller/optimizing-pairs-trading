from clickhouse_driver import Client
import numpy as np
from scipy.optimize import minimize
from scipy import stats
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial

def calculate_spread(price1, price2):
   x1_norm = price1 / price1[0]
   x2_norm = price2 / price2[0]
   
   def neg_log_likelihood(params):
       beta, sigma_r = params
       n = len(x1_norm)
       rt = llh = 0
       
       for t in range(1, n):
           pred = beta * x1_norm[t] + rt
           innov = x2_norm[t] - pred
           var = sigma_r ** 2
           llh += -0.5 * (np.log(var) + innov ** 2 / var)
           rt += innov
       return -llh

   beta_init = np.cov(x1_norm, x2_norm)[0,1] / np.var(x1_norm)
   std_init = np.std(x2_norm - beta_init * x1_norm)
   
   result = minimize(
       neg_log_likelihood,
       x0=[beta_init, std_init],
       bounds=[(-2, 2), (1e-6, 1)],
       method='L-BFGS-B'
   )
   
   beta = result.x[0] * price2[0] / price1[0]
   return x2_norm - beta * x1_norm, beta

def calculate_lr_stat(x1_norm, x2_norm):    
   def compute_full_likelihood(params):
       beta, rho, sigma_m, sigma_r = params
       n = len(x1_norm)
       mt = rt = llh = 0
       
       for t in range(1, n):
           mt = rho * mt
           pred = beta * x1_norm[t] + mt + rt
           innov = x2_norm[t] - pred
           var = sigma_m**2 * (1-rho**2) + sigma_r**2
           llh += -0.5 * (np.log(var) + innov**2/var)
           rt += innov * 0.001
       return -llh

   beta_init = np.cov(x1_norm, x2_norm)[0,1] / np.var(x1_norm)
   std_init = np.std(x2_norm - beta_init * x1_norm)
   
   result = minimize(
       compute_full_likelihood,
       x0=[beta_init, 0.9, std_init*0.5, std_init*0.5],
       bounds=[(-2, 2), (0.6, 0.99), (0.1, 1), (0.1, 1)],
       method='L-BFGS-B',
       options={'maxiter': 100, 'ftol': 1e-4}
   )
   
   return -2 * result.fun, result.x[1], result.x[2], result.x[3]

def calculate_pci(price1, price2):
   x1_norm = price1 / price1[0]
   x2_norm = price2 / price2[0]
   
   lr_stat, rho, sigma_m, sigma_r = calculate_lr_stat(x1_norm, x2_norm)
   r_squared = (2 * sigma_m**2) / (2 * sigma_m**2 + sigma_r**2 * (1 + rho))
   
   return rho, r_squared, lr_stat

def calculate_insample_sharpe(prices1, prices2, rho, beta, formation_end):
    if formation_end >= len(prices1) or formation_end <= 0:
        return 0.0
    
    # Calculate spread and normalize
    spread = prices2 - beta * prices1
    formation_spread = spread[:formation_end]
    if len(formation_spread) == 0:
        return 0.0
        
    mean_spread = np.mean(formation_spread)
    std_spread = np.std(formation_spread)
    if std_spread == 0:
        return 0.0
    
    # Initialize arrays for the trading period
    trading_period = len(prices1) - formation_end
    pos = np.zeros(trading_period)
    returns = []
    z_scores = (spread[formation_end:] - mean_spread) / std_spread
    
    # Track position changes and returns
    position_changes = 0
    total_signals = 0
    
    # Calculate positions for trading period
    for i in range(trading_period):
        t = i + formation_end
        z_score = z_scores[i]
        
        # Count signals that cross thresholds
        if abs(z_score) > 1.0:
            total_signals += 1
        
        # For first position
        if i == 0:
            if z_score > 1.0:
                pos[i] = -1
                position_changes += 1
            elif z_score < -1.0:
                pos[i] = 1
                position_changes += 1
        # For subsequent positions
        else:
            prev_pos = pos[i-1]
            if prev_pos == 0:  # No position
                if z_score > 1.0:
                    pos[i] = -1
                    position_changes += 1
                elif z_score < -1.0:
                    pos[i] = 1
                    position_changes += 1
                else:
                    pos[i] = 0
            else:  # Existing position
                if (prev_pos > 0 and z_score > -0.5) or (prev_pos < 0 and z_score < 0.5):
                    pos[i] = 0
                    position_changes += 1
                else:
                    pos[i] = prev_pos
        
        # Calculate returns when position changes
        if i > 0 and pos[i] != pos[i-1]:
            price_ratio1 = prices1[t]/prices1[t-1]
            price_ratio2 = prices2[t]/prices2[t-1]
            hedge_ratio = beta * prices1[t] / prices2[t]
            ret = pos[i] * (price_ratio1 - hedge_ratio * price_ratio2)
            
            # Debug print for non-zero returns
            if abs(ret) > 0:
                print(f"Return: {ret:.4f}, Pos: {pos[i]}, Price1 ratio: {price_ratio1:.4f}, Price2 ratio: {price_ratio2:.4f}")
            
            returns.append(ret)
    
    # Debug information
    print("\nSpread Statistics:")
    print(f"Formation period length: {formation_end}")
    print(f"Mean spread: {mean_spread:.6f}")
    print(f"Std spread: {std_spread:.6f}")
    print(f"Min z-score: {min(z_scores):.2f}")
    print(f"Max z-score: {max(z_scores):.2f}")
    print(f"Z-scores > 1: {np.sum(z_scores > 1)}")
    print(f"Z-scores < -1: {np.sum(z_scores < -1)}")
    
    print("\nTrading Statistics:")
    print(f"Trading period length: {trading_period}")
    print(f"Total threshold crossings: {total_signals}")
    print(f"Total position changes: {position_changes}")
    print(f"Number of returns: {len(returns)}")
    
    if returns:
        returns_array = np.array(returns)
        print("\nReturn Statistics:")
        print(f"Mean return: {np.mean(returns_array):.6f}")
        print(f"Std return: {np.std(returns_array):.6f}")
        print(f"Min return: {np.min(returns_array):.6f}")
        print(f"Max return: {np.max(returns_array):.6f}")
            
    if not returns:
        return 0.0
        
    returns = np.array(returns)
    if len(returns) < 2:
        return 0.0
        
    return np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0

def process_pair(data):
   pair_key, period_start, prices1, prices2, formation_end = data
   try:
       prices1, prices2 = np.array(prices1), np.array(prices2)
       if not (np.all(np.isfinite(prices1)) and np.all(np.isfinite(prices2))):
           return None
           
       spread, beta = calculate_spread(prices1, prices2)
       rho, r_squared, lr_stat = calculate_pci(prices1, prices2)
       
       return (
           pair_key, 
           period_start, 
           float(rho), 
           float(r_squared), 
           float(lr_stat),
           float(beta),
           0.0,  # placeholder for in_sample_sharpe
           lr_stat
       )
   except:
       return None

def batch_insert(client, results, batch_size=1000):
   for i in range(0, len(results), batch_size):
       batch = results[i:i + batch_size]
       client.execute('INSERT INTO pci_results VALUES', batch)

def run_pci_tests():
    client = Client(host='localhost', port=9000, user='default', password='password')

    client.execute('DROP TABLE IF EXISTS pci_results')
    client.execute('''
    CREATE TABLE IF NOT EXISTS pci_results
    (
        pair_key String,
        period_start Date,
        rho Float64,
        r_squared Float64,
        lr_score Float64,
        beta Float64,
        in_sample_sharpe Float64,
        passed Boolean
    ) ENGINE = MergeTree()
    ORDER BY (pair_key, period_start)
    ''')

    print("Note: in_sample_sharpe will be calculated in a separate step after Kalman filter results")

    pairs_data = client.execute('''
        SELECT 
            fp.pair_key,
            fp.period_start,
            groupArray(fp.price1) as prices1,
            groupArray(fp.price2) as prices2,
            toUInt32(indexOf(groupArray(fp.date), p.formation_end)) as formation_end
        FROM formation_prices fp
        JOIN formation_periods p ON fp.pair_key = p.pair_key AND fp.period_start = p.period_start
        GROUP BY fp.pair_key, fp.period_start, p.formation_end
        HAVING count(*) >= 252
    ''')

    print(f"Processing {len(pairs_data)} pairs...")

    with Pool() as pool:
        results = list(tqdm(
            pool.imap(process_pair, pairs_data, chunksize=10),
            total=len(pairs_data)
        ))

    valid_results = [r for r in results if r is not None]
    lr_scores = [r[7] for r in valid_results]

    if valid_results:
        print(f"Calculating final results for {len(valid_results)} pairs...")
        lr_threshold = np.percentile(lr_scores, 5)
        
        final_results = [
            (
                r[0], r[1], r[2], r[3], r[4], r[5], r[6],
                r[2] > 0.5 and r[3] > 0.5 and r[4] < lr_threshold
            )
            for r in valid_results
        ]
        
        print("Inserting results into database...")
        batch_insert(client, final_results)
        print("Done!")

if __name__ == "__main__":
   run_pci_tests()
