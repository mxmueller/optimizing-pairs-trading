"""
Trading simulator module for pairs trading strategies.
This module provides functionality to simulate trading operations with various costs and metrics calculation.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict, Any

def calculate_max_drawdown(capital_series: pd.Series) -> float:
    """
    Calculate the maximum drawdown from peak in percentage.
    
    Args:
        capital_series: Series of capital values over time
        
    Returns:
        float: Maximum drawdown in percentage
    """
    peak = capital_series.expanding(min_periods=1).max()
    drawdown = (capital_series - peak) / peak
    return drawdown.min() * 100

def calculate_pair_metrics(closed_trades: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate performance metrics for each trading pair.
    
    Args:
        closed_trades: DataFrame containing closed trade information
        
    Returns:
        Dict containing metrics for each pair
    """
    pair_metrics = {}
    for pair in closed_trades['pair'].unique():
        pair_trades = closed_trades[closed_trades['pair'] == pair]
        pair_metrics[pair] = {
            'total_trades': len(pair_trades),
            'win_rate': (pair_trades['pnl'] > 0).mean() * 100,
            'total_pnl': pair_trades['pnl'].sum(),
            'avg_profit': pair_trades['pnl'].mean(),
            'avg_hold_time': pair_trades['hold_time'].mean()
        }
    return pair_metrics

def calculate_metrics(trades_df: pd.DataFrame, daily_returns_df: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
    """
    Calculate comprehensive trading metrics.
    
    Args:
        trades_df: DataFrame containing all trades
        daily_returns_df: DataFrame containing daily returns
        initial_capital: Initial trading capital
        
    Returns:
        Dict containing calculated metrics
    """
    closed_trades = trades_df[trades_df['type'] == 'CLOSE']
    
    metrics = {
        'total_trades': len(trades_df[trades_df['type'] == 'OPEN']),
        'total_pnl': closed_trades['pnl'].sum(),
        'end_capital': trades_df['capital'].iloc[-1],
        'total_return': (trades_df['capital'].iloc[-1] / initial_capital - 1) * 100,
        'win_rate': (closed_trades['pnl'] > 0).mean() * 100,
        'avg_profit_per_trade': closed_trades['pnl'].mean(),
        'avg_win': closed_trades[closed_trades['pnl'] > 0]['pnl'].mean(),
        'avg_loss': closed_trades[closed_trades['pnl'] < 0]['pnl'].mean(),
        'largest_win': closed_trades['pnl'].max(),
        'largest_loss': closed_trades['pnl'].min(),
        'profit_factor': abs(closed_trades[closed_trades['pnl'] > 0]['pnl'].sum() / 
                           closed_trades[closed_trades['pnl'] < 0]['pnl'].sum()),
        'avg_hold_time': closed_trades['hold_time'].mean(),
        'total_transaction_costs': trades_df['transaction_costs'].sum(),
        'avg_transaction_costs': trades_df['transaction_costs'].mean()
    }
    
    daily_returns = daily_returns_df['return']
    metrics.update({
        'sharpe_ratio': np.sqrt(252) * (daily_returns.mean() / daily_returns.std()),
        'volatility_annual': daily_returns.std() * np.sqrt(252) * 100,
        'max_drawdown': calculate_max_drawdown(trades_df['capital']),
        'skewness': stats.skew(daily_returns),
        'kurtosis': stats.kurtosis(daily_returns)
    })
    
    pair_metrics = calculate_pair_metrics(closed_trades)
    metrics['pair_metrics'] = pair_metrics
    
    return metrics

def simulate_trading(
    trades_df: pd.DataFrame,
    initial_capital: float = 10000,
    commission_per_share: float = 0.005,
    variable_fee: float = 0.00018,
    bid_ask_spread: float = 0.0002,
    price_impact_coef: float = 0.002,
    risk_per_trade: float = 0.01
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Simulate trading operations with transaction costs and position tracking.
    
    Args:
        trades_df: DataFrame containing trading signals
        initial_capital: Starting capital for trading
        commission_per_share: Fixed commission per share traded
        variable_fee: Percentage-based fee per trade
        bid_ask_spread: Estimated bid-ask spread cost
        price_impact_coef: Coefficient for price impact calculation
        
    Returns:
        Tuple containing:
            - DataFrame with trade history
            - Dict with performance metrics
    """
    capital = initial_capital
    positions = {}
    trades_history = []
    daily_returns = []
    last_date = None
    daily_capital = initial_capital
    
    for _, trade in trades_df.iterrows():
        if last_date is None:
            last_date = trade['date']
        elif trade['date'] != last_date:
            daily_returns.append({
                'date': last_date,
                'return': (capital - daily_capital) / daily_capital
            })
            daily_capital = capital
            last_date = trade['date']
            
        risk_amount = capital * risk_per_trade
        s1_symbol, s2_symbol = trade['pair'].split('-')
        
        if trade['pair'] in positions:
            old_pos = positions[trade['pair']]
            pnl = 0
            hold_time = trade['date'] - old_pos['entry_date']
            
            if old_pos['type'] == 'LONG':
                s1_pnl = old_pos['s1_shares'] * (trade['S1_price'] - old_pos['s1_entry'])
                s2_pnl = old_pos['s2_shares'] * (old_pos['s2_entry'] - trade['S2_price'])
                pnl = s1_pnl + s2_pnl
            else:
                s1_pnl = old_pos['s1_shares'] * (old_pos['s1_entry'] - trade['S1_price'])
                s2_pnl = old_pos['s2_shares'] * (trade['S2_price'] - old_pos['s2_entry'])
                pnl = s1_pnl + s2_pnl
            
            s1_trade_value = old_pos['s1_shares'] * trade['S1_price']
            s2_trade_value = old_pos['s2_shares'] * trade['S2_price']
            total_value = s1_trade_value + s2_trade_value
            
            commission_cost = (old_pos['s1_shares'] + old_pos['s2_shares']) * commission_per_share
            variable_cost = total_value * variable_fee
            spread_cost = total_value * bid_ask_spread
            price_impact = total_value * price_impact_coef * np.sqrt(total_value/1000000)
            total_costs = commission_cost + variable_cost + spread_cost + price_impact
            
            capital += pnl - total_costs
            del positions[trade['pair']]
            
            trades_history.append({
                'date': trade['date'],
                'pair': trade['pair'],
                'type': 'CLOSE',
                'pnl': pnl,
                'capital': capital,
                'transaction_costs': total_costs,
                'hold_time': hold_time.total_seconds() / 3600,
                'return': pnl / risk_amount
            })
        
        if trade['action'] in ['LONG', 'SHORT']:
            s1_shares = risk_amount / trade['S1_price']
            s2_shares = s1_shares * trade['ratio']
            
            s1_trade_value = s1_shares * trade['S1_price']
            s2_trade_value = s2_shares * trade['S2_price']
            total_value = s1_trade_value + s2_trade_value
            
            commission_cost = (s1_shares + s2_shares) * commission_per_share
            variable_cost = total_value * variable_fee
            spread_cost = total_value * bid_ask_spread
            price_impact = total_value * price_impact_coef * np.sqrt(total_value/1000000)
            total_costs = commission_cost + variable_cost + spread_cost + price_impact
            
            cost_adjustment = 1 - (total_costs / risk_amount)
            s1_shares *= cost_adjustment
            s2_shares *= cost_adjustment
            
            positions[trade['pair']] = {
                'type': trade['action'],
                's1_shares': s1_shares,
                's2_shares': s2_shares,
                's1_entry': trade['S1_price'],
                's2_entry': trade['S2_price'],
                'entry_date': trade['date']
            }
            
            trades_history.append({
                'date': trade['date'],
                'pair': trade['pair'],
                'type': 'OPEN',
                'action': trade['action'],
                'capital': capital,
                'transaction_costs': total_costs,
                's1_shares': s1_shares,
                's2_shares': s2_shares,
                's1_price': trade['S1_price'],
                's2_price': trade['S2_price']
            })
    
    trades_df = pd.DataFrame(trades_history)
    daily_returns_df = pd.DataFrame(daily_returns)
    
    metrics = calculate_metrics(trades_df, daily_returns_df, initial_capital)
    
    return trades_df, metrics

def print_trading_summary(metrics: Dict[str, Any]) -> None:
    """
    Print a formatted summary of trading metrics.
    
    Args:
        metrics: Dict containing trading metrics
    """
    print("=== Grundlegende Metriken ===")
    print(f"Endkapital: ${metrics['end_capital']:.2f}")
    print(f"Gesamtrendite: {metrics['total_return']:.2f}%")
    print(f"Anzahl Trades: {metrics['total_trades']}")
    
    print("\n=== Performance Metriken ===")
    print(f"Win Rate: {metrics['win_rate']:.2f}%")
    print(f"Profit Faktor: {metrics['profit_factor']:.2f}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Jährliche Volatilität: {metrics['volatility_annual']:.2f}%")
    
    print("\n=== Trade Statistiken ===")
    print(f"Durchschn. Gewinn: ${metrics['avg_win']:.2f}")
    print(f"Durchschn. Verlust: ${metrics['avg_loss']:.2f}")
    print(f"Größter Gewinn: ${metrics['largest_win']:.2f}")
    print(f"Größter Verlust: ${metrics['largest_loss']:.2f}")
    print(f"Durchschn. Haltezeit: {metrics['avg_hold_time']:.2f} Stunden")
    
    print("\n=== Kosten ===")
    print(f"Gesamte Transaktionskosten: ${metrics['total_transaction_costs']:.2f}")
    print(f"Durchschn. Kosten/Trade: ${metrics['avg_transaction_costs']:.2f}")
    
    print("\n=== Verteilungsmetriken ===")
    print(f"Schiefe: {metrics['skewness']:.2f}")
    print(f"Kurtosis: {metrics['kurtosis']:.2f}")
    
    print("\n=== Performance nach Pairs ===")
    for pair, pair_metric in metrics['pair_metrics'].items():
        print(f"\n{pair}:")
        print(f"Trades: {pair_metric['total_trades']}")
        print(f"Win Rate: {pair_metric['win_rate']:.2f}%")
        print(f"Gesamt P&L: ${pair_metric['total_pnl']:.2f}")
        print(f"Durchschn. Profit: ${pair_metric['avg_profit']:.2f}")
        print(f"Durchschn. Haltezeit: {pair_metric['avg_hold_time']:.2f} Stunden")