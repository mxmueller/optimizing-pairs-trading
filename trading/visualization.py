import streamlit as st
from backtesting import BacktestConfig, PairBacktest, MultiStrategyBacktest
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide")

st.title('Pairs Trading Backtest Analysis')

with st.sidebar:
    st.header('Backtest Configuration')
    initial_capital = st.number_input('Initial Capital', value=100000, step=10000)
    trade_percentage = st.slider('Trade Size (%)', 0.0, 1.0, 0.1, 0.01)
    commission_per_share = st.number_input('Commission per Share', value=0.005, step=0.001, format="%.3f")
    variable_fee = st.number_input('Variable Fee', value=0.00018, step=0.0001, format="%.5f")
    bid_ask_spread = st.number_input('Bid-Ask Spread', value=0.0002, step=0.0001, format="%.4f")
    price_impact_coef = st.number_input('Price Impact Coefficient', value=0.002, step=0.001, format="%.3f")
    
    st.header('Strategy Selection')
    available_strategies = PairBacktest.get_available_strategies()
    selected_strategy = st.selectbox('Select Strategy', list(available_strategies.keys()))

config = BacktestConfig(
    initial_capital=initial_capital,
    trade_percentage=trade_percentage,
    commission_per_share=commission_per_share,
    variable_fee=variable_fee,
    bid_ask_spread=bid_ask_spread,
    price_impact_coef=price_impact_coef
)

multi_backtest = MultiStrategyBacktest(config=config)

single_backtest = PairBacktest(
    config=config,
    signals_path=available_strategies[selected_strategy]
)

if single_backtest.validate_data():
    single_backtest.calculate_trade_pnl()
    single_backtest.calculate_equity_curve()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        'Strategy Comparison', 
        'Single Strategy Analysis', 
        'Portfolio Overview', 
        'Trade Statistics', 
        'Cost Analysis', 
        'Recent Trades',
        'Trade Details'
    ])

    with tab1:
        st.header('Strategy Comparison')
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(multi_backtest.plot_all_equity_curves(), use_container_width=True)
        
        with col2:
            metrics_df = multi_backtest.get_strategy_metrics()
            st.dataframe(metrics_df.style.format({
                'Final Equity': '${:,.2f}',
                'Total Return %': '{:.2f}%',
                'Win Rate %': '{:.2f}%',
                'Avg Trade': '${:.2f}',
                'Num Trades': '{:,.0f}'
            }))

    with tab2:
        st.header('Single Strategy Analysis')
        st.plotly_chart(single_backtest.plot_equity_curve(), use_container_width=True)

    with tab3:
        st.header('Portfolio Overview')
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Initial Capital", f"${config.initial_capital:,.2f}")
            st.metric("Final Capital (without costs)", f"${single_backtest.equity_curve['equity_raw'].iloc[-1]:,.2f}")
            st.metric("Total Return (without costs)", f"{((single_backtest.equity_curve['equity_raw'].iloc[-1] / config.initial_capital - 1) * 100):.2f}%")
            st.metric("Trade Size (% of Capital)", f"{(config.trade_percentage * 100):.1f}%")
        
        with col2:
            st.metric("Number of Trades", len(single_backtest.trades_pnl))
            st.metric("Final Capital (with costs)", f"${single_backtest.equity_curve['equity_net'].iloc[-1]:,.2f}")
            st.metric("Total Return (with costs)", f"{((single_backtest.equity_curve['equity_net'].iloc[-1] / config.initial_capital - 1) * 100):.2f}%")
            st.metric("Date Range", f"{single_backtest.equity_curve['date'].iloc[0].strftime('%Y-%m-%d')} to {single_backtest.equity_curve['date'].iloc[-1].strftime('%Y-%m-%d')}")

    with tab4:
        st.header('Trade Statistics')
        
        winning_trades_raw = single_backtest.trades_pnl[single_backtest.trades_pnl['pnl_raw'] > 0]
        losing_trades_raw = single_backtest.trades_pnl[single_backtest.trades_pnl['pnl_raw'] <= 0]
        winning_trades_net = single_backtest.trades_pnl[single_backtest.trades_pnl['pnl_net'] > 0]
        losing_trades_net = single_backtest.trades_pnl[single_backtest.trades_pnl['pnl_net'] <= 0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Win Rate (without costs)", f"{(len(winning_trades_raw) / len(single_backtest.trades_pnl) * 100):.2f}%")
            st.metric("Average Win (without costs)", f"${winning_trades_raw['pnl_raw'].mean():,.2f}")
            st.metric("Average Loss (without costs)", f"${losing_trades_raw['pnl_raw'].mean():,.2f}")
            st.metric("Average Trade (without costs)", f"${single_backtest.trades_pnl['pnl_raw'].mean():,.2f}")
        
        with col2:
            st.metric("Win Rate (with costs)", f"{(len(winning_trades_net) / len(single_backtest.trades_pnl) * 100):.2f}%")
            st.metric("Average Win (with costs)", f"${winning_trades_net['pnl_net'].mean():,.2f}")
            st.metric("Average Loss (with costs)", f"${losing_trades_net['pnl_net'].mean():,.2f}")
            st.metric("Average Trade (with costs)", f"${single_backtest.trades_pnl['pnl_net'].mean():,.2f}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 5 Winning Trades")
            top_winners = single_backtest.trades_pnl.nlargest(5, 'pnl_net')[
                ['symbol', 'entry_date', 'exit_date', 'pnl_net']
            ]
            st.dataframe(top_winners.style.format({
                'pnl_net': '${:,.2f}',
                'entry_date': '{:%Y-%m-%d}',
                'exit_date': '{:%Y-%m-%d}'
            }))
            
        with col2:
            st.subheader("Top 5 Losing Trades")
            top_losers = single_backtest.trades_pnl.nsmallest(5, 'pnl_net')[
                ['symbol', 'entry_date', 'exit_date', 'pnl_net']
            ]
            st.dataframe(top_losers.style.format({
                'pnl_net': '${:,.2f}',
                'entry_date': '{:%Y-%m-%d}',
                'exit_date': '{:%Y-%m-%d}'
            }))

        st.subheader("Trade Duration Analysis")
        single_backtest.trades_pnl['duration'] = (
            single_backtest.trades_pnl['exit_date'] - single_backtest.trades_pnl['entry_date']
        ).dt.days
        
        fig_duration = go.Figure()
        fig_duration.add_trace(go.Histogram(x=single_backtest.trades_pnl['duration']))
        fig_duration.update_layout(
            title="Distribution of Trade Durations",
            xaxis_title="Duration (days)",
            yaxis_title="Number of Trades",
            showlegend=False
        )
        st.plotly_chart(fig_duration, use_container_width=True)

    with tab5:
        st.header('Trading Costs Analysis')
        
        total_costs = single_backtest.trades_pnl[
            ['commission', 'variable_cost', 'spread_cost', 'price_impact', 'total_cost']
        ].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Commission", f"${total_costs['commission']:,.2f}")
            st.metric("Total Variable Fees", f"${total_costs['variable_cost']:,.2f}")
            st.metric("Total Spread Costs", f"${total_costs['spread_cost']:,.2f}")
        
        with col2:
            st.metric("Total Price Impact", f"${total_costs['price_impact']:,.2f}")
            st.metric("Total Trading Costs", f"${total_costs['total_cost']:,.2f}")
            st.metric("Average Cost per Trade", f"${(total_costs['total_cost'] / len(single_backtest.trades_pnl)):,.2f}")
        
        st.metric("Costs as % of Raw PnL", f"{(total_costs['total_cost'] / abs(single_backtest.trades_pnl['pnl_raw'].sum()) * 100):,.2f}%")

        cost_data = total_costs[['commission', 'variable_cost', 'spread_cost', 'price_impact']]
        fig_costs = go.Figure(data=[go.Pie(
            labels=cost_data.index,
            values=cost_data.values,
            hole=.3
        )])
        fig_costs.update_layout(title="Trading Costs Distribution")
        st.plotly_chart(fig_costs, use_container_width=True)

    with tab6:
        st.header('Recent Trades')
        
        col1, col2 = st.columns(2)
        with col1:
            trade_filter = st.selectbox(
                "Filter trades by",
                ["All", "Winning", "Losing"]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Most Recent", "Highest PnL", "Lowest PnL"]
            )

        if trade_filter == "Winning":
            filtered_trades = single_backtest.trades_pnl[single_backtest.trades_pnl['pnl_net'] > 0]
        elif trade_filter == "Losing":
            filtered_trades = single_backtest.trades_pnl[single_backtest.trades_pnl['pnl_net'] <= 0]
        else:
            filtered_trades = single_backtest.trades_pnl

        if sort_by == "Most Recent":
            filtered_trades = filtered_trades.sort_values('exit_date', ascending=False)
        elif sort_by == "Highest PnL":
            filtered_trades = filtered_trades.sort_values('pnl_net', ascending=False)
        else:
            filtered_trades = filtered_trades.sort_values('pnl_net', ascending=True)

        trades_to_display = filtered_trades[
            ['symbol', 'position_type', 'entry_date', 'exit_date', 'pnl_raw', 'total_cost', 'pnl_net']
        ].head(10)

        st.dataframe(trades_to_display.style.format({
            'entry_date': '{:%Y-%m-%d}',
            'exit_date': '{:%Y-%m-%d}',
            'pnl_raw': '${:,.2f}',
            'total_cost': '${:.2f}',
            'pnl_net': '${:.2f}'
        }))
        
    with tab7:
        st.header('Trade Details')
        
        traded_symbols = single_backtest.trades_pnl['symbol'].unique()
        selected_symbol = st.selectbox('Select Symbol', traded_symbols)
        
        symbol_data = single_backtest.market_data[
            single_backtest.market_data['symbol'] == selected_symbol
        ].copy()
        
        symbol_trades = single_backtest.trades_pnl[
            single_backtest.trades_pnl['symbol'] == selected_symbol
        ].copy()
        
        if not symbol_data.empty and not symbol_trades.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=symbol_data['date'],
                y=symbol_data['close'],
                mode='lines',
                name='Price',
                line=dict(color='gray')
            ))
            
            for pos_type in ['long', 'short']:
                mask = symbol_trades['position_type'] == pos_type
                if mask.any():
                    fig.add_trace(go.Scatter(
                        x=symbol_trades[mask]['entry_date'],
                        y=symbol_trades[mask]['entry_price'],
                        mode='markers',
                        name=f'{pos_type.capitalize()} Entry',
                        marker=dict(
                            symbol='triangle-up' if pos_type == 'long' else 'triangle-down',
                            size=12,
                            color='green' if pos_type == 'long' else 'red'
                        )
                    ))
            
            if 'exit_type' in symbol_trades.columns:
                for exit_type in symbol_trades['exit_type'].unique():
                    mask = symbol_trades['exit_type'] == exit_type
                    if mask.any():
                        fig.add_trace(go.Scatter(
                            x=symbol_trades[mask]['exit_date'],
                            y=symbol_trades[mask]['exit_price'],
                            mode='markers',
                            name=f'Exit ({exit_type})',
                            marker=dict(
                                symbol='circle',
                                size=10,
                                color='blue' if exit_type == 'target' else 'orange'
                            )
                        ))
            else:
                fig.add_trace(go.Scatter(
                    x=symbol_trades['exit_date'],
                    y=symbol_trades['exit_price'],
                    mode='markers',
                    name='Exit',
                    marker=dict(
                        symbol='circle',
                        size=10,
                        color='blue'
                    )
                ))
            
            fig.update_layout(
                title=f'Trade History - {selected_symbol}',
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_white',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader('Trade Details')
            trade_details = symbol_trades[[
                'entry_date', 'entry_price', 
                'exit_date', 'exit_price',
                'position_type', 'pnl_net'
            ]].copy()
            
            if 'exit_type' in symbol_trades.columns:
                trade_details['exit_type'] = symbol_trades['exit_type']
                
            st.dataframe(trade_details.style.format({
                'entry_date': '{:%Y-%m-%d}',
                'exit_date': '{:%Y-%m-%d}',
                'entry_price': '${:.2f}',
                'exit_price': '${:.2f}',
                'pnl_net': '${:.2f}'
            }))