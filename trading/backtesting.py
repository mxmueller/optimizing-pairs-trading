import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import os
import glob

class BacktestConfig:
    def __init__(self, 
                 initial_capital=100000, 
                 trade_percentage=0.1,
                 commission_per_share=0.005,
                 variable_fee=0.00018,
                 bid_ask_spread=0.0002,
                 price_impact_coef=0.002):
        self.initial_capital = initial_capital
        self.trade_percentage = trade_percentage
        self.commission_per_share = commission_per_share
        self.variable_fee = variable_fee
        self.bid_ask_spread = bid_ask_spread
        self.price_impact_coef = price_impact_coef

class PairBacktest:
    def __init__(self, config=None, signals_path=None, market_data_path='../notebooks/sim_daily.parquet'):
        self.config = config if config else BacktestConfig()
        if signals_path:
            self.signals = pd.read_parquet(signals_path)
            self.strategy_name = os.path.splitext(os.path.basename(signals_path))[0]
        else:
            self.signals = None
            self.strategy_name = None
            
        self.market_data = pd.read_parquet(market_data_path)
        
        if self.signals is not None:
            self.signals['entry_date'] = pd.to_datetime(self.signals['entry_date'], unit='ms')
            self.signals['exit_date'] = pd.to_datetime(self.signals['exit_date'], unit='ms')
            self.signals = self.signals.sort_values('entry_date')
            
        self.market_data['date'] = pd.to_datetime(self.market_data['date'])
        self.market_data = self.market_data.sort_values('date')
        
        self.trades_pnl = None
        self.equity_curve = None

    @staticmethod
    def get_available_strategies(directory='../notebooks/results/'):
        files = glob.glob(os.path.join(directory, '*.parquet'))
        return {os.path.splitext(os.path.basename(f))[0]: f for f in files}
        
    def calculate_trading_costs(self, row):
        commission = row['units'] * self.config.commission_per_share
        variable_cost = (row['units'] * row['entry_price']) * self.config.variable_fee
        spread_cost = (row['units'] * row['entry_price'] * self.config.bid_ask_spread) * 2
        price_impact = (row['units'] * row['entry_price']) * self.config.price_impact_coef
        total_cost = commission + variable_cost + spread_cost + price_impact
        
        return pd.Series({
            'commission': commission,
            'variable_cost': variable_cost,
            'spread_cost': spread_cost,
            'price_impact': price_impact,
            'total_cost': total_cost
        })
    
    def calculate_trade_pnl(self):
        self.trades_pnl = self.signals.copy()
        trade_size = self.config.initial_capital * self.config.trade_percentage
        
        self.trades_pnl['trade_size'] = trade_size
        self.trades_pnl['units'] = self.trades_pnl['trade_size'] / self.trades_pnl['entry_price']
        
        self.trades_pnl['pnl_raw'] = np.where(
            self.trades_pnl['position_type'] == 'long',
            (self.trades_pnl['exit_price'] - self.trades_pnl['entry_price']) * self.trades_pnl['units'],
            (self.trades_pnl['entry_price'] - self.trades_pnl['exit_price']) * self.trades_pnl['units']
        )
        
        costs_df = self.trades_pnl.apply(self.calculate_trading_costs, axis=1)
        self.trades_pnl = pd.concat([self.trades_pnl, costs_df], axis=1)
        
        self.trades_pnl['pnl_net'] = self.trades_pnl['pnl_raw'] - self.trades_pnl['total_cost']
        self.trades_pnl['return_raw'] = self.trades_pnl['pnl_raw'] / self.trades_pnl['trade_size']
        self.trades_pnl['return_net'] = self.trades_pnl['pnl_net'] / self.trades_pnl['trade_size']
        
        return self.trades_pnl
    
    def calculate_equity_curve(self):
        if self.trades_pnl is None:
            self.calculate_trade_pnl()
            
        equity = pd.DataFrame()
        equity['date'] = pd.concat([
            self.trades_pnl['entry_date'],
            self.trades_pnl['exit_date']
        ]).unique()
        equity = equity.sort_values('date')
        
        cumulative_pnl_raw = []
        cumulative_pnl_net = []
        current_capital_raw = self.config.initial_capital
        current_capital_net = self.config.initial_capital
        
        for date in equity['date']:
            closed_trades = self.trades_pnl[self.trades_pnl['exit_date'] <= date]
            if not closed_trades.empty:
                current_capital_raw = self.config.initial_capital + closed_trades['pnl_raw'].sum()
                current_capital_net = self.config.initial_capital + closed_trades['pnl_net'].sum()
            cumulative_pnl_raw.append(current_capital_raw)
            cumulative_pnl_net.append(current_capital_net)
            
        equity['equity_raw'] = cumulative_pnl_raw
        equity['equity_net'] = cumulative_pnl_net
        self.equity_curve = equity
        return self.equity_curve

    def plot_equity_curve(self):
        if self.equity_curve is None:
            self.calculate_equity_curve()
            
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.equity_curve['date'],
            y=self.equity_curve['equity_raw'],
            mode='lines',
            name=f'{self.strategy_name} (without costs)',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.equity_curve['date'],
            y=self.equity_curve['equity_net'],
            mode='lines',
            name=f'{self.strategy_name} (with costs)',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title='Portfolio Equity Curve',
            xaxis_title='Date',
            yaxis_title='Equity',
            template='plotly_white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig

    def validate_data(self):
        valid = True
        if self.signals is None or self.signals.empty or self.market_data.empty:
            valid = False
            
        required_signal_cols = ['trade_id', 'symbol', 'entry_date', 'entry_price', 
                            'exit_date', 'exit_price', 'position_type', 'paired_symbol']
        if not all(col in self.signals.columns for col in required_signal_cols):
            valid = False
            
        required_market_cols = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in self.market_data.columns for col in required_market_cols):
            valid = False
            
        return valid

class MultiStrategyBacktest:
    def __init__(self, config=None, market_data_path='../notebooks/nasdaq_daily.parquet'):
        self.config = config if config else BacktestConfig()
        self.market_data_path = market_data_path
        self.strategies = {}
        self.load_all_strategies()
        
    def load_all_strategies(self):
        strategy_files = PairBacktest.get_available_strategies()
        for name, file_path in strategy_files.items():
            backtest = PairBacktest(
                config=self.config,
                signals_path=file_path,
                market_data_path=self.market_data_path
            )
            if backtest.validate_data():
                self.strategies[name] = backtest
                
    def plot_all_equity_curves(self):
        fig = go.Figure()
        
        for name, backtest in self.strategies.items():
            if backtest.equity_curve is None:
                backtest.calculate_equity_curve()
                
            fig.add_trace(go.Scatter(
                x=backtest.equity_curve['date'],
                y=backtest.equity_curve['equity_net'],
                mode='lines',
                name=name
            ))
            
        fig.update_layout(
            title='Strategy Comparison',
            xaxis_title='Date',
            yaxis_title='Equity (with costs)',
            template='plotly_white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
        
    def get_strategy_metrics(self):
        metrics = []
        
        for name, backtest in self.strategies.items():
            if backtest.trades_pnl is None:
                backtest.calculate_trade_pnl()
                
            equity = backtest.equity_curve['equity_net'].iloc[-1]
            total_return = (equity / self.config.initial_capital - 1) * 100
            win_rate = (len(backtest.trades_pnl[backtest.trades_pnl['pnl_net'] > 0]) / len(backtest.trades_pnl) * 100)
            avg_trade = backtest.trades_pnl['pnl_net'].mean()
            
            metrics.append({
                'Strategy': name,
                'Final Equity': equity,
                'Total Return %': total_return,
                'Win Rate %': win_rate,
                'Avg Trade': avg_trade,
                'Num Trades': len(backtest.trades_pnl)
            })
            
        return pd.DataFrame(metrics)