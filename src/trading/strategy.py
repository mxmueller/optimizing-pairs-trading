import pandas as pd
import plotly.graph_objects as go
from config import BacktestConfig
from pair import PairBacktest

class MultiStrategyBacktest:
    def __init__(self, config=None, market_data_path='../../data/raw/nasdaq_daily.parquet'):
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