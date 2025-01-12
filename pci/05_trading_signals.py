from clickhouse_driver import Client
import numpy as np
import pandas as pd

class PairTrading:
    def __init__(self, tau_open=1.0, tau_close=-0.5):
        self.client = Client(host='localhost', port=9000, user='default', password='password')
        self.tau_open = tau_open
        self.tau_close = tau_close
        self.stopped_pairs = {}  # Track pairs that hit stop-loss

    def debug_data(self, pair_key, formation_end, period_end):
        kalman_data = self.client.execute(f'''
            SELECT COUNT(*) 
            FROM kalman_results
            WHERE pair_key = '{pair_key}'
            AND date BETWEEN '{formation_end}' AND '{period_end}'
        ''')
        print(f"Kalman results count: {kalman_data[0][0]}")
        
        price_data = self.client.execute(f'''
            SELECT COUNT(*)
            FROM formation_prices
            WHERE pair_key = '{pair_key}'
            AND date BETWEEN '{formation_end}' AND '{period_end}'
        ''')
        print(f"Price data count: {price_data[0][0]}")
        
        beta_data = self.client.execute(f'''
            SELECT beta
            FROM pci_results
            WHERE pair_key = '{pair_key}'
        ''')
        print(f"Beta value: {beta_data[0][0] if beta_data else 'Not found'}")

    def get_formation_sigma(self, pair_key, formation_end):
        formation_data = self.client.execute(f'''
            SELECT 
                avg(mt) as mean_mt,
                stddevPop(mt) as std_mt
            FROM kalman_results
            WHERE pair_key = '{pair_key}'
            AND date <= '{formation_end}'
        ''')
        if not formation_data or not formation_data[0]:
            return None
        return {"mean": formation_data[0][0], "std": formation_data[0][1]}

    def calculate_signals(self, pair_key, formation_end, period_end):
        self.debug_data(pair_key, formation_end, period_end)
        
        formation_stats = self.get_formation_sigma(pair_key, formation_end)
        if formation_stats is None:
            return [], []
        
        period_key = f"{pair_key}_{formation_end}"
        if period_key in self.stopped_pairs:
            return [], []
        
        trading_data = self.client.execute(f'''
            SELECT k.date, k.mt, k.rt, p.price1, p.price2, pr.beta
            FROM kalman_results k
            JOIN formation_periods fp ON k.pair_key = fp.pair_key
            JOIN formation_prices p ON k.pair_key = p.pair_key AND k.date = p.date
            JOIN pci_results pr ON k.pair_key = pr.pair_key
            WHERE k.pair_key = '{pair_key}'
            AND k.date BETWEEN '{formation_end}' AND '{period_end}'
            ORDER BY k.date
        ''')

        if not trading_data:
            return [], []
        
        position = 0
        entry_price1 = entry_price2 = None
        signals = []
        trades = []
        current_trade = None
        initial_portfolio_value = 1.0
        current_portfolio_value = initial_portfolio_value

        for date, mt, rt, price1, price2, beta in trading_data:
            z_score = (mt - formation_stats["mean"]) / formation_stats["std"]
            hedge_ratio = beta * price1 / price2

            if position != 0:
                pos1_value = position * (price1 - entry_price1)
                pos2_value = -position * hedge_ratio * (price2 - entry_price2)
                current_portfolio_value = initial_portfolio_value + pos1_value + pos2_value
                
                if current_portfolio_value < 0.9 * initial_portfolio_value:
                    if current_trade:
                        current_trade.update({
                            'exit_date': date,
                            'exit_z': z_score,
                            'exit_price1': price1,
                            'exit_price2': price2,
                            'pnl': current_portfolio_value - initial_portfolio_value,
                            'exit_type': 'stop_loss'
                        })
                        trades.append(current_trade)
                        self.stopped_pairs[period_key] = date
                    position = 0
                    current_trade = None
                    continue

            if position == 0:
                if z_score < -self.tau_open:
                    position = 1
                    entry_price1, entry_price2 = price1, price2
                    current_trade = {
                        'entry_date': date,
                        'entry_z': z_score,
                        'type': 'long',
                        'entry_price1': price1,
                        'entry_price2': price2
                    }
                elif z_score > self.tau_open:
                    position = -1
                    entry_price1, entry_price2 = price1, price2
                    current_trade = {
                        'entry_date': date,
                        'entry_z': z_score,
                        'type': 'short',
                        'entry_price1': price1,
                        'entry_price2': price2
                    }
            elif position != 0:
                if (position > 0 and z_score > -self.tau_close) or \
                (position < 0 and z_score < self.tau_close):
                    pos1_value = position * (price1 - entry_price1)
                    pos2_value = -position * hedge_ratio * (price2 - entry_price2)
                    total_pnl = pos1_value + pos2_value
                    
                    if current_trade:
                        current_trade.update({
                            'exit_date': date,
                            'exit_z': z_score,
                            'exit_price1': price1,
                            'exit_price2': price2,
                            'pnl': total_pnl,
                            'exit_type': 'target'
                        })
                        trades.append(current_trade)
                    position = 0
                    current_trade = None

            signals.append({
                'date': date,
                'z_score': z_score,
                'position': position,
                'hedge_ratio': hedge_ratio,
                'portfolio_value': current_portfolio_value
            })

        return signals, trades

def validate_signals(signals, trades):
    if not signals:
        return
        
    z_scores = [s['z_score'] for s in signals]
    print(f"Z-Score Stats - Mean: {np.mean(z_scores):.3f}, Std: {np.std(z_scores):.3f}")
    
    if trades:
        pnls = [t['pnl'] for t in trades]
        durations = [(pd.to_datetime(t['exit_date']) - pd.to_datetime(t['entry_date'])).days for t in trades]
        print(f"Trades: {len(trades)}, Avg PnL: {np.mean(pnls):.3f}, Win Rate: {len([p for p in pnls if p > 0])/len(pnls):.2%}")
        print(f"Avg Duration: {np.mean(durations):.1f} days")

def main():
    trader = PairTrading()
    
    # Select top performing pairs based on multiple criteria:
    # - Good historical performance (positive Sharpe ratio)
    # - Strong correlation and model fit
    # - Reasonable volatility (avoid extreme z-scores)
    # - Sufficient trading activity in formation period
    # - Correct formation period (48 months) and trading period (6 months)
    test_pairs = trader.client.execute('''
        SELECT
            p.pair_key,
            p.period_start,
            p.formation_end,
            p.period_end
        FROM formation_periods p
        JOIN pci_results pr ON p.pair_key = pr.pair_key
        WHERE pr.passed = 1
        ORDER BY pr.in_sample_sharpe DESC
        LIMIT 20;
    ''')
    
    print(f"Trading top {len(test_pairs)} pairs")
    
    for pair_key, period_start, formation_end, period_end in test_pairs:
        print(f"\nPair: {pair_key}")
        signals, trades = trader.calculate_signals(pair_key, formation_end, period_end)
        validate_signals(signals, trades)

if __name__ == "__main__":
    main()
