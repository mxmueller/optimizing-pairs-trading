import pandas as pd
import numpy as np
import plotly.graph_objects as go
from tabulate import tabulate
from datetime import datetime

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
    def __init__(self, config=None, signals_path='../notebooks/results/cointegration_bollinger_results.parquet', 
                 market_data_path='../notebooks/nasdaq_daily.parquet'):
        self.config = config if config else BacktestConfig()
        self.signals = pd.read_parquet(signals_path)
        self.market_data = pd.read_parquet(market_data_path)
        
        self.signals['entry_date'] = pd.to_datetime(self.signals['entry_date'], unit='ms')
        self.signals['exit_date'] = pd.to_datetime(self.signals['exit_date'], unit='ms')
        self.market_data['date'] = pd.to_datetime(self.market_data['date'])
        
        self.signals = self.signals.sort_values('entry_date')
        self.market_data = self.market_data.sort_values('date')
        
        self.trades_pnl = None
        self.equity_curve = None
        
    def calculate_trading_costs(self, row):
        # Fixed commission per share
        commission = row['units'] * self.config.commission_per_share
        
        # Variable fee based on trade value
        variable_cost = (row['units'] * row['entry_price']) * self.config.variable_fee
        
        # Bid-ask spread cost (both entry and exit)
        spread_cost = (row['units'] * row['entry_price'] * self.config.bid_ask_spread) * 2
        
        # Price impact cost (based on trade size relative to average volume)
        # Simplified price impact model
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
        
        # Calculate raw PnL without costs
        self.trades_pnl['pnl_raw'] = np.where(
            self.trades_pnl['position_type'] == 'long',
            (self.trades_pnl['exit_price'] - self.trades_pnl['entry_price']) * self.trades_pnl['units'],
            (self.trades_pnl['entry_price'] - self.trades_pnl['exit_price']) * self.trades_pnl['units']
        )
        
        # Calculate trading costs
        costs_df = self.trades_pnl.apply(self.calculate_trading_costs, axis=1)
        self.trades_pnl = pd.concat([self.trades_pnl, costs_df], axis=1)
        
        # Calculate net PnL after costs
        self.trades_pnl['pnl_net'] = self.trades_pnl['pnl_raw'] - self.trades_pnl['total_cost']
        
        # Calculate returns
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
        
        # Calculate both raw and net equity curves
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
        
        # Plot both raw and net equity curves
        fig.add_trace(go.Scatter(
            x=self.equity_curve['date'],
            y=self.equity_curve['equity_raw'],
            mode='lines',
            name='Equity (without costs)',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.equity_curve['date'],
            y=self.equity_curve['equity_net'],
            mode='lines',
            name='Equity (with costs)',
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

    def print_metrics(self):
        if self.trades_pnl is None:
            self.calculate_trade_pnl()
        if self.equity_curve is None:
            self.calculate_equity_curve()

        # Portfolio Overview
        portfolio_metrics = {
            'Initial Capital': f"${self.config.initial_capital:,.2f}",
            'Final Capital (without costs)': f"${self.equity_curve['equity_raw'].iloc[-1]:,.2f}",
            'Final Capital (with costs)': f"${self.equity_curve['equity_net'].iloc[-1]:,.2f}",
            'Total Return (without costs)': f"{((self.equity_curve['equity_raw'].iloc[-1] / self.config.initial_capital - 1) * 100):.2f}%",
            'Total Return (with costs)': f"{((self.equity_curve['equity_net'].iloc[-1] / self.config.initial_capital - 1) * 100):.2f}%",
            'Trade Size (% of Capital)': f"{(self.config.trade_percentage * 100):.1f}%",
            'Number of Trades': len(self.trades_pnl),
            'Date Range': f"{self.equity_curve['date'].iloc[0].strftime('%Y-%m-%d')} to {self.equity_curve['date'].iloc[-1].strftime('%Y-%m-%d')}"
        }

        # Trade Statistics
        winning_trades_raw = self.trades_pnl[self.trades_pnl['pnl_raw'] > 0]
        losing_trades_raw = self.trades_pnl[self.trades_pnl['pnl_raw'] <= 0]
        winning_trades_net = self.trades_pnl[self.trades_pnl['pnl_net'] > 0]
        losing_trades_net = self.trades_pnl[self.trades_pnl['pnl_net'] <= 0]
        
        trade_metrics = {
            'Win Rate (without costs)': f"{(len(winning_trades_raw) / len(self.trades_pnl) * 100):.2f}%",
            'Win Rate (with costs)': f"{(len(winning_trades_net) / len(self.trades_pnl) * 100):.2f}%",
            'Average Win (without costs)': f"${winning_trades_raw['pnl_raw'].mean():,.2f}",
            'Average Win (with costs)': f"${winning_trades_net['pnl_net'].mean():,.2f}",
            'Average Loss (without costs)': f"${losing_trades_raw['pnl_raw'].mean():,.2f}",
            'Average Loss (with costs)': f"${losing_trades_net['pnl_net'].mean():,.2f}",
            'Average Trade (without costs)': f"${self.trades_pnl['pnl_raw'].mean():,.2f}",
            'Average Trade (with costs)': f"${self.trades_pnl['pnl_net'].mean():,.2f}"
        }

        # Cost Analysis
        total_costs = self.trades_pnl[['commission', 'variable_cost', 'spread_cost', 'price_impact', 'total_cost']].sum()
        cost_metrics = {
            'Total Commission': f"${total_costs['commission']:,.2f}",
            'Total Variable Fees': f"${total_costs['variable_cost']:,.2f}",
            'Total Spread Costs': f"${total_costs['spread_cost']:,.2f}",
            'Total Price Impact': f"${total_costs['price_impact']:,.2f}",
            'Total Trading Costs': f"${total_costs['total_cost']:,.2f}",
            'Average Cost per Trade': f"${(total_costs['total_cost'] / len(self.trades_pnl)):,.2f}",
            'Costs as % of Raw PnL': f"{(total_costs['total_cost'] / abs(self.trades_pnl['pnl_raw'].sum()) * 100):,.2f}%"
        }

        # Print tables
        print("\nPortfolio Overview")
        print("="* 50)
        overview_table = [[k, v] for k, v in portfolio_metrics.items()]
        print(tabulate(overview_table, headers=['Metric', 'Value'], tablefmt='grid'))
        
        print("\nTrade Statistics")
        print("="* 50)
        trade_table = [[k, v] for k, v in trade_metrics.items()]
        print(tabulate(trade_table, headers=['Metric', 'Value'], tablefmt='grid'))
        
        print("\nTrading Costs Analysis")
        print("="* 50)
        cost_table = [[k, v] for k, v in cost_metrics.items()]
        print(tabulate(cost_table, headers=['Metric', 'Value'], tablefmt='grid'))

        # Print Recent Trades
        print("\nMost Recent Trades (with costs)")
        print("="* 50)
        recent_trades = self.trades_pnl.sort_values('exit_date', ascending=False).head(5)[
            ['symbol', 'position_type', 'entry_date', 'exit_date', 'pnl_raw', 'total_cost', 'pnl_net']
        ].copy()
        
        recent_trades['entry_date'] = recent_trades['entry_date'].dt.strftime('%Y-%m-%d')
        recent_trades['exit_date'] = recent_trades['exit_date'].dt.strftime('%Y-%m-%d')
        recent_trades['pnl_raw'] = recent_trades['pnl_raw'].apply(lambda x: f"${x:,.2f}")
        recent_trades['total_cost'] = recent_trades['total_cost'].apply(lambda x: f"${x:,.2f}")
        recent_trades['pnl_net'] = recent_trades['pnl_net'].apply(lambda x: f"${x:,.2f}")
        
        print(tabulate(recent_trades, headers='keys', tablefmt='grid'))

    def validate_data(self):
        valid = True
        if self.signals.empty or self.market_data.empty:
            print("Error: Empty DataFrames")
            valid = False
            
        required_signal_cols = ['trade_id', 'symbol', 'entry_date', 'entry_price', 
                            'exit_date', 'exit_price', 'position_type', 'paired_symbol']
        if not all(col in self.signals.columns for col in required_signal_cols):
            print("Error: Missing columns in signals")
            valid = False
            
        required_market_cols = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in self.market_data.columns for col in required_market_cols):
            print("Error: Missing columns in market data")
            valid = False
            
        return valid

if __name__ == "__main__":
    custom_config = BacktestConfig(
        initial_capital=100000,
        trade_percentage=0.01,
        commission_per_share=0.005,
        variable_fee=0.00018,
        bid_ask_spread=0.0002,
        price_impact_coef=0.002
    )
    
    backtest = PairBacktest(config=custom_config)
    
    if backtest.validate_data():
        backtest.calculate_trade_pnl()
        
        # Print metrics
        backtest.print_metrics()
        
        # Show equity curve
        equity_plot = backtest.plot_equity_curve()
        equity_plot.show()