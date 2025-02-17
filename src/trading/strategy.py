import pandas as pd
import numpy as np
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

    def calculate_metrics(self, backtest):
        if backtest.trades_pnl is None:
            backtest.calculate_trade_pnl()

        if backtest.equity_curve is None:
            backtest.calculate_equity_curve()

        equity = backtest.equity_curve['equity_net'].iloc[-1]
        total_return = (equity / self.config.initial_capital - 1) * 100

        trades = backtest.trades_pnl
        equity_curve = backtest.equity_curve

        # Basic Metrics
        win_rate = (len(trades[trades['pnl_net'] > 0]) / len(trades) * 100)
        avg_trade = trades['pnl_net'].mean()

        # Risk Metrics
        rolling_equity = equity_curve['equity_net']
        rolling_max = rolling_equity.expanding().max()
        drawdowns = (rolling_equity - rolling_max) / rolling_max * 100
        max_drawdown = abs(drawdowns.min())

        # Returns for Ratios
        trade_returns = trades['return_net']  # Verwende Trade-Renditen direkt
        # returns = equity_curve['equity_net'].pct_change().dropna() # Entferne diese Zeile

        print(
            f"\nTrade Returns Series for {backtest.strategy_name}:\n{trade_returns.head(20)}")  # Print first 20 trade returns
        std_returns = trade_returns.std()
        print(
            f"Standard Deviation of Trade Returns for {backtest.strategy_name}: {std_returns}")  # Print std of trade returns

        excess_returns = trade_returns - 0.02 / 252  # Assuming 2% risk-free rate
        negative_returns = trade_returns[trade_returns < 0]

        std_returns = trade_returns.std()  # Berechne Standardabweichung der Trade-Renditen
        std_negative_returns = negative_returns.std()  # Berechne Standardabweichung der negativen Trade-Renditen

        sharpe = np.sqrt(252) * (
                    trade_returns.mean() / std_returns) if std_returns != 0 else 0  # Verwende trade_returns
        sortino = np.sqrt(252) * (trade_returns.mean() / std_negative_returns) if len(
            negative_returns) > 0 and std_negative_returns != 0 else None  # Verwende trade_returns und korrigierte Sortino Berechnung

        # Trade Performance
        gross_profit = trades[trades['pnl_net'] > 0]['pnl_net'].sum()
        gross_loss = abs(trades[trades['pnl_net'] < 0]['pnl_net'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')

        avg_win = trades[trades['pnl_net'] > 0]['pnl_net'].mean()
        avg_loss = abs(trades[trades['pnl_net'] < 0]['pnl_net'].mean())
        win_loss_ratio = avg_win / avg_loss if avg_loss != 0 else float('inf')

        # Streaks
        trades['win'] = trades['pnl_net'] > 0
        trades['streak'] = (trades['win'] != trades['win'].shift()).cumsum()
        win_streaks = trades[trades['win']].groupby('streak').size()
        loss_streaks = trades[~trades['win']].groupby('streak').size()

        max_win_streak = win_streaks.max() if not win_streaks.empty else 0
        max_loss_streak = loss_streaks.max() if not loss_streaks.empty else 0

        # Time Analysis
        trades['duration'] = (trades['exit_date'] - trades['entry_date']).dt.days
        avg_duration = trades['duration'].mean()

        trades['month'] = trades['exit_date'].dt.to_period('M')
        monthly_returns = trades.groupby('month')['pnl_net'].sum()
        best_month = monthly_returns.max()
        worst_month = monthly_returns.min()
        avg_trades_per_month = len(trades) / len(monthly_returns)

        return {
            'Strategy': backtest.strategy_name,
            'Final Equity': equity,
            'Total Return %': total_return,
            'Win Rate %': win_rate,
            'Avg Trade': avg_trade,
            'Num Trades': len(trades),
            'Max Drawdown %': max_drawdown,
            'Sharpe Ratio': sharpe,
            'Sortino Ratio': sortino,
            'Return/Drawdown': abs(total_return / max_drawdown) if max_drawdown != 0 else float('inf'),
            'Profit Factor': profit_factor,
            'Win/Loss Ratio': win_loss_ratio,
            'Max Win Streak': max_win_streak,
            'Max Loss Streak': max_loss_streak,
            'Avg Duration (days)': avg_duration,
            'Trades per Month': avg_trades_per_month,
            'Best Month': best_month,
            'Worst Month': worst_month
        }
        
    def get_strategy_metrics(self):
        metrics = []
        for name, backtest in self.strategies.items():
            metrics.append(self.calculate_metrics(backtest))
        return pd.DataFrame(metrics)