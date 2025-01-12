from clickhouse_driver import Client
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool

def calculate_log_likelihood(prices1, prices2, beta, rho, sigma_x, sigma_m, sigma_r):
    n = len(prices1)
    prices1_norm = prices1 / prices1[0]
    prices2_norm = prices2 / prices2[0]
    
    state = np.zeros((3, n))
    P = np.zeros((3, 3, n))
    
    H = np.array([[beta, 1, 1], [1, 0, 0]])
    F = np.array([[1, 0, 0], [0, rho, 0], [0, 0, 1]])
    Q = np.diag([sigma_x**2, sigma_m**2, sigma_r**2])
    R = np.array([[1e-6, 0], [0, 1e-6]])
    
    log_likelihood = 0
    
    state[:, 0] = [prices1_norm[0], 0, prices2_norm[0] - beta * prices1_norm[0]]
    P[:, :, 0] = Q
    
    for t in range(1, n):
        state_pred = F @ state[:, t-1]
        P_pred = F @ P[:, :, t-1] @ F.T + Q
        
        y = np.array([[prices2_norm[t]], [prices1_norm[t]]])
        
        innovation = y - H @ state_pred.reshape(-1, 1)
        S = H @ P_pred @ H.T + R
        
        K = P_pred @ H.T @ np.linalg.inv(S)
        
        state[:, t] = state_pred + (K @ innovation).flatten()
        P[:, :, t] = (np.eye(3) - K @ H) @ P_pred
        
        log_likelihood += -0.5 * (np.log(np.linalg.det(2 * np.pi * S)) + 
                                innovation.T @ np.linalg.inv(S) @ innovation)[0,0]
    
    return log_likelihood

def optimize_parameters(prices1, prices2, beta, rho, initial_sigma_x=1.0, initial_sigma_m=1.0, initial_sigma_r=1.0):
    from scipy.optimize import minimize
    
    def objective(params):
        sigma_x, sigma_m, sigma_r = params
        return -calculate_log_likelihood(prices1, prices2, beta, rho, sigma_x, sigma_m, sigma_r)
    
    result = minimize(
        objective,
        x0=[initial_sigma_x, initial_sigma_m, initial_sigma_r],
        bounds=[(1e-6, None), (1e-6, None), (1e-6, None)],
        method='L-BFGS-B'
    )
    
    return result.x[0], result.x[1], result.x[2]

def calculate_kalman_gain(beta, rho, sigma_x, sigma_m, sigma_r):
    H = np.array([[beta, 1, 1], [1, 0, 0]])
    F = np.array([[1, 0, 0], [0, rho, 0], [0, 0, 1]])
    Q = np.diag([sigma_x**2, sigma_m**2, sigma_r**2])
    R = np.array([[1e-6, 0], [0, 1e-6]])
    
    P = Q
    for _ in range(100):
        P_pred = F @ P @ F.T + Q
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)
        P = (np.eye(3) - K @ H) @ P_pred
    
    return K

def apply_kalman_filter(prices1, prices2, beta, rho, K):
    prices1_norm = prices1 / prices1[0]
    prices2_norm = prices2 / prices2[0]
    
    n = len(prices1_norm)
    state = np.zeros((3, n))
    
    H = np.array([[beta, 1, 1], [1, 0, 0]])
    F = np.array([[1, 0, 0], [0, rho, 0], [0, 0, 1]])
    
    state[:, 0] = [prices1_norm[0], 0, prices2_norm[0] - beta * prices1_norm[0]]
    
    for t in range(1, n):
        state_pred = F @ state[:, t-1]
        y = np.array([[prices2_norm[t]], [prices1_norm[t]]])
        innovation = y - H @ state_pred.reshape(-1, 1)
        state[:, t] = state_pred + (K @ innovation).flatten()
    
    return state[1, :], state[2, :]

def process_single_pair(pair_data):
    client = Client(host='localhost', port=9000, user='default', password='password')
    pair_key, beta, rho, period_start, sym1, sym2 = pair_data
    
    prices = client.execute(f'''
        SELECT p1.date, p1.close as price1, p2.close as price2
        FROM stock_data p1
        JOIN stock_data p2 ON p1.date = p2.date
        WHERE p1.symbol = '{sym1}' 
        AND p2.symbol = '{sym2}'
        AND p1.date >= '{period_start}'
        ORDER BY p1.date
    ''')
    
    if not prices:
        return None
        
    dates = [p[0] for p in prices]
    price1 = np.array([p[1] for p in prices])
    price2 = np.array([p[2] for p in prices])
    
    sigma_x, sigma_m, sigma_r = optimize_parameters(price1, price2, beta, rho)
    K = calculate_kalman_gain(beta, rho, sigma_x, sigma_m, sigma_r)
    
    if K is None:
        return None
        
    mt, rt = apply_kalman_filter(price1, price2, beta, rho, K)
    
    return [(pair_key, date, m, r, sigma_x, sigma_m, sigma_r) 
            for date, m, r in zip(dates, mt, rt)]

def process_pairs():
    client = Client(host='localhost', port=9000, user='default', password='password')
    
    client.execute('''
    CREATE TABLE IF NOT EXISTS kalman_results
    (
        pair_key String,
        date Date,
        mt Float64,
        rt Float64,
        sigma_x Float64,
        sigma_m Float64,
        sigma_r Float64
    ) ENGINE = MergeTree()
    ORDER BY (pair_key, date)
    ''')

    pairs = client.execute('''
        SELECT DISTINCT pr.pair_key, pr.beta, pr.rho, 
               pr.period_start, fp.symbol1, fp.symbol2
        FROM pci_results pr
        JOIN formation_periods fp ON pr.pair_key = fp.pair_key 
        WHERE pr.passed = 1
    ''')

    with Pool() as pool:
        results = list(tqdm(pool.imap(process_single_pair, pairs), total=len(pairs)))
    
    results = [r for r in results if r is not None]
    flat_results = [item for sublist in results for item in sublist]
    
    if flat_results:
        client.execute('INSERT INTO kalman_results VALUES', flat_results)

if __name__ == "__main__":
    process_pairs()