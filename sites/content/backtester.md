---
title: "Backtester"
math: true  # Das aktiviert KaTeX (ist schon im Theme)
toc: true
readTime: true

---


## Configuration Sidebar
The Configuration Sidebar serves as the central control panel for the backtesting application. All analyses rely on these settings.

{{< anchor "window" >}}
{{< figure src="/images/gif/config.gif" 
          >}}

### Market & Strategy
The first step involves selecting a market from the `Select Market` dropdown. This choice determines which stocks and strategies become available. After market selection, the `Select Strategy` dropdown displays only compatible strategies. Without a valid selection, the application shows "No strategies available for selected market".

### Parameters & Costs
The **Trading Parameters** include **Initial Capital** (starting capital for the simulation, defaults to `$100,000` with a minimum of `$1,000`) and **Position Size** as a percentage of capital allocated per position (defaults to `1.0%`, ranging from `0.1%` to `10.0%`). Position Size controls both risk exposure and the number of simultaneous positions.

The expandable **Trading Costs** section covers four key cost parameters: **Fixed Commission** (defaults to `$1.00`) as a flat fee per trade, **Variable Fee** (defaults to `0.018%`) as a percentage of trade value, **Bid-Ask Spread** (defaults to `0.1%`) representing the bid-ask spread, and **Risk-Free Rate** (defaults to `0.0%`) used for Sharpe ratio calculations. All parameter changes take effect immediately across all analysis tabs. These tabs become accessible only after selecting both market and strategy.
****
## Market Overview
The Market Overview tab provides a quick overview of the selected market and enables comparison of individual stocks.

{{< anchor "window" >}}
{{< figure src="/images/gif/overview.gif" 
          >}}

### Market Index
The left side displays the **Market Index** as a time series chart showing the current index value and absolute change since inception. The **Current** metric shows the current index value, while the green/red number indicates the total change. The chart visualizes the historical development of the market index over the available time period. Below this is the **Symbol Comparison** section. Up to 5 stocks can be selected from the `Compare symbols` multiselect to compare their price development. The resulting line chart displays the closing prices of all selected symbols over time, with different colors for each stock.

### Symbol List
The right column contains the **Symbols** list with all available stocks of the selected market. The display `Total: X` shows the total number of symbols. The scrollable table displays all symbols in alphabetical order and serves as a reference for available stocks in the market. All data is based on the market selected in the Configuration Sidebar and updates automatically when the market changes.
****

## Symbol Analysis
The Symbol Analysis tab compares the trading strategy with a Buy & Hold strategy for individual stocks and displays detailed trade information.

{{< anchor "window" >}}
{{< figure src="/images/gif/symbol.gif" 
          >}}
### Chart Analysis
A stock can be selected from the `Select Symbol` dropdown. The upper chart displays three lines: the **Price History** (golden line) showing the historical price movement, the **Buy & Hold Return** (green line) as the percentage return of a simple buy-and-hold strategy, and the **Trading Strategy Return** (magenta line) as the cumulative return of the selected trading strategy. The lower chart visualizes individual trades with **Profitable Trades** (blue dots) and **Losing Trades** (red dots). Each dot represents a trade with its individual return. A dashed gray line at 0% separates profitable from losing trades.

### Trade Details & Performance
Below the charts is the complete **All Trades** table containing all executed trades, sortable by date, entry/exit prices, performance, and trade type. The table shows `entry_date`, `exit_date`, `position_type`, `entry_price`, `exit_price`, `performance`, and `exit_type`. The **Symbol Trades** section displays basic metrics such as `Total Trades` and `Win Rate`. Additionally, detailed performance metrics are shown: `Total Performance`, `Avg Performance`, `Max Gain`, and `Max Loss` of the selected stock based on the configured trading parameters.

****

## Strategy Performance
The Strategy Performance tab analyzes the overall performance of the selected trading strategy with detailed time series and metrics.
{{< anchor "window" >}}
{{< figure src="/images/gif/performance.gif" 
          >}}
### Performance Over Time
The left side displays the **Portfolio Equity Curve** as the main chart showing the development of total capital over time. The blue line represents `Total Capital`, while a dashed red line marks the `Initial Capital`. Below this, the **Daily Profit/Loss** chart appears as a bar chart, where green bars represent profitable days and red bars represent losing days. Three metrics summarize the key results: `Cumulative P&L` as absolute profit/loss, `Net P&L (after costs)` after deducting all trading costs, and `Total Return` as the percentage total return. The **Active Positions Over Time** chart additionally shows the number of simultaneous positions throughout the trading period.

### Performance Metrics
The right column contains key metrics such as `Total Trades`, `Final Capital` with percentage change, `Win Rate`, `Profitable Days`, `Sharpe Ratio`, and `Max Drawdown`. Three tabs organize the detailed metrics: **Performance** displays `Total Performance`, `Avg Performance`, `Max Gain/Loss`, and trade statistics. **Costs** lists `Total Costs`, `Avg Cost per Trade`, and a breakdown by entry/exit costs (Commission, Variable Fee, Spread). **Portfolio** shows capital metrics such as `Initial/Final/Max/Min Capital` as well as `Current Invested` and `Current Available`.

****

## Pairs Analysis
The Pairs Analysis tab analyzes pair-trading strategies for selected stock pairs within specific trading windows.
{{< anchor "window" >}}
{{< figure src="/images/gif/pair.gif" 
          >}}

### Symbol Selection & Trades
The analysis begins with selecting a **Trading Window** from the dropdown, which determines the analysis period. Subsequently, the two-column selection involves choosing the **first symbol** (left) and **second symbol** (right). The dropdowns display only stocks that were actually traded within this window.

The **Trades Visualization** displays a statistics line showing `Total Trades`, `Profit Trades`, `Loss Trades`, and `Break-Even` trades for the selected pair. Below are **Display Options** for switching between "Active Trade Periods Only" and "All Data". The timeline charts for both symbols visualize entry points (blue triangles), exit points (colored circles based on outcome), and connecting lines between entry/exit. The **Trades Details** table lists all pair trades with date, prices, performance, and trade type.

### Pairs Overview
The **Pairs Overview** section displays a metrics line with `Window`, `Total Pairs`, `Total Trades`, and `Selected Pair` information. The **Top 20 Pairs** bar chart visualizes the most active pairs by number of trades, color-coded by trading volume. The complete pairs table below lists all available pairs for the window sorted by trade count, with columns `Pair`, `Symbol 1`, `Symbol 2`, and `Trades`.

****

## Strategy Comparison
The Strategy Comparison tab enables direct comparison of multiple trading strategies and provides comprehensive export functions for statistical analysis.
{{< anchor "window" >}}
{{< figure src="/images/gif/last.gif" 
          >}}
### Performance Metrics
At least 2 strategies must be selected from the `Select Strategies to Compare` multiselect. The comparison table displays `Total Return`, `Sharpe Ratio`, `Max Drawdown`, `Win Rate`, `Total Trades`, and `Profitable Days` for all selected strategies. Below this, separate bar charts for each metric provide visual comparisons.

### Equity Curves & Returns
The **Equity Curves** tab visualizes the capital development of all strategies in a combined chart with different colors per strategy and a dashed line representing the initial capital. **Returns Distribution** shows overlaid histograms of daily returns for all strategies and a statistics table with `Mean Return`, `Std Dev`, `Min/Max Return`, and `Positive Days` for each strategy.

### Drawdowns Analysis
A time series chart displays all drawdowns with an inverted Y-axis (deeper drawdowns positioned lower) and a bar chart showing maximum drawdowns per strategy. Drawdowns are represented as negative percentage points.

### Pair Analysis
After trading window selection, a table shows all pairs with trade counts per strategy. **Common Pairs** lists pairs that appear across all strategies. For selected common pairs, detailed performance comparisons are visualized with `Total Return`, `Win Rate`, `Total Trades`, and `Avg Trade Return` as bar charts.

### Export
**Performance Summary** exports all metrics and trading parameters as CSV. **Timeseries Data** contains daily capital values for all strategies. **Pairs Analysis** provides detailed pair performance data after window selection. Additionally, code examples for statistical analyses such as t-tests, consistency analyses, and Sharpe ratio calculations are provided.

****

## Strategy Creator Tab
The Strategy Creator enables automated creation of trading strategies through the execution of preconfigured Jupyter Notebooks with customizable parameters.
{{< anchor "window" >}}
{{< figure src="/images/gif/fin.gif" 
          >}}
### Workflow 
The Strategy Creator provides a structured process for strategy creation. The workflow begins with selecting the desired market and strategy template from the available Jupyter Notebooks. Parameters are automatically extracted from the notebook and displayed as input fields, which can be adjusted according to requirements. A meaningful name for the strategy is assigned through **Strategy Type** and **Strategy Description**. The **Output Filename** is generated automatically but can be manually adjusted. After clicking **"Run Strategy Creation"**, a background job starts that executes the notebook with the configured parameters. The execution process runs entirely in the background: First, market data is downloaded from MinIO Storage, then the Jupyter Notebook is executed with the configured parameters, and finally the generated strategy file is uploaded back to storage with appropriate metadata tags. The page can be left during execution as jobs continue running.

### Job Monitoring 
After clicking **"Run Strategy Creation"**, a background job is initiated. The **Active Jobs** table displays all running and completed jobs with color-coded status pills: `pending` (yellow), `running` (blue), `completed` (green), and `failed` (red). Additionally, progress information and status messages are shown. Jobs progress through the following phases: downloading market data from MinIO, notebook execution with configured parameters, uploading the generated strategy file back to MinIO with corresponding metadata tags. The **"Refresh Jobs"** button manually updates the job list, while automatic updates occur every 10 requests.
****

## Strategy Templates & Parameter Guide
Overview of available trading strategies and their configurable parameters.

### Cointegration Z-Score Evolution
This strategy identifies cointegrated stock pairs and trades based on Z-score thresholds. The `p_threshold` (default: 0.05) determines the significance level for the cointegration test, where lower values indicate stricter pair selection. The `min_pairs` (20) sets the minimum number of pairs to trade per window, while `window_shifts` (12) defines the number of rolling analysis windows for walk-forward backtesting. Trading signals are controlled by `entry_threshold` (2.0) and `exit_threshold` (0.5) as Z-score thresholds. For Z-score calculation, `window1` (5) serves as the short moving average and `window2` (60) as the long moving average. The `shift_size` (1) determines the shift between analysis windows in months.

### Cointegration with Bollinger Bands
This variant uses Bollinger Bands instead of fixed Z-score thresholds for more dynamic trading signals. The `std_dev` (2.0) acts as the standard deviation multiplier for the Bollinger Bands, while `exit_std_dev` (0.5) defines the exit threshold. The `window_size` (20) determines the calculation window for the Bollinger Bands. Additionally, hedge ratios are dynamically adjusted: `hr_window` (25) defines the recalculation window and `hr_recalc` (3) the recalculation interval in days. This enables better adaptation to changing market conditions.

### Affinity Propagation Clustering with Z-Score
This method uses clustering for pair discovery instead of direct cointegration. The strategy combines cluster analysis with classical Z-score trading signals. The parameters `entry_threshold` (2.0) and `exit_threshold` (0.5) function like the standard Z-score strategy, but pairs are intelligently pre-sorted through clustering, which can lead to more stable trading relationships.

### Affinity Propagation with Bollinger Bands
This strategy combines clustering-based pair discovery with Bollinger Band signals. The `std_dev` (2) and `exit_std_dev` (0.5) parameters control the Bollinger Band width for entry and exit signals. The `window` (50) defines the calculation window for the Bollinger Bands. Dynamic hedge ratio adjustment occurs through `hr_window` (25) and `hr_recalc` (3), which is particularly important for cluster-based pairs as they may exhibit different beta relationships.

### Gradient Boosting Z-Score Evolution
This machine learning-based strategy uses gradient boosting for intelligent pair prioritization. The ML parameters include `learning_rate` (0.2) for learning speed, `max_depth` (2) for maximum tree depth to prevent overfitting, as well as `min_samples_leaf` (2) and `min_samples_split` (2) to control tree complexity. The `n_estimators` (300) parameter determines the number of trees in the ensemble. The model learns from historical data which pairs deliver the best trading results and prioritizes them accordingly.

### Gradient Boosting with Bollinger Bands
This strategy combines ML-based pair selection with Bollinger Band trading. The `bb_window` (50) defines the Bollinger Band window, while `std_dev` (1.5) uses a more conservative multiplier than other strategies. The gradient boosting parameters are identical to the Z-score variant, but the model is trained on Bollinger Band-specific features, which can lead to more precise entry and exit timing.
