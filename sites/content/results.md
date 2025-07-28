---
title: "Results"
math: true  # Das aktiviert KaTeX (ist schon im Theme)
readTime: true
---

The following evaluation of results examines the hypothesis: *Machine learning-based approaches for pair identification outperform traditional cointegration-based methods in pairs trading.* In contrast to cointegration-based methods, the pairs identified through machine learning approaches with their respective strategies beat the market ($F_{100}$: +7.9%, $N_{100}$: +15.8% for the year 2024).

## Performance on the $N_{100}$ Index
On the $N_{100}$, the Gradient Boost Regressor achieved 20.90% annual return (Z-Score) with a Sharpe ratio of 6.16. This corresponds to a market outperformance of 5.1 percentage points compared to the $N_{100}$ Index. The Affinity Propagation approach achieved 17.98% with a Sharpe ratio of 7.48. Traditional cointegration approaches, by contrast, reached -1.13% or showed double-digit losses.

| Ansatz | Strategy | Return (%) | Sharpe Ratio | Max Drawdown (%) |
|--------|----------|------------|--------------|------------------|
| Gradient Boost | Z-Score | 20.90 | 6.16 | -0.11 |
| Gradient Boost | Bollinger | 20.47 | 6.73 | -0.18 |
| Affinity Propagation | Z-Score | 17.98 | 7.48 | -0.09 |
| Affinity Propagation | Bollinger | 13.53 | 7.01 | -0.05 |
| Kointegration | Z-Score | -1.13 | 1.03 | -3.87 |
| Kointegration | Bollinger | -11.21 | 0.63 | -11.99 |

{{< anchor "nasdaq-rolling" >}}
{{< figure src="/images/lala.png" 
           caption="Rolling window analysis of strategy performance on the $N_{100}$ Index with 252-day window. Machine learning methods show consistently positive performance, while cointegration approaches exhibit volatile patterns."
          >}}
{{< anchor "nasdaq-heatmap" >}}
{{< figure src="/images/2.png" 
           caption="Monthly performance heatmap of the six trading strategies on the $N_{100}$ Index for 2024. The visualization illustrates the different market adaptation of the algorithms. Color scale from red (underperformance) to green (outperformance)."
          >}}

## Performance on the $F_{100}$ Index
On the $F_{100}$, both machine learning methods generated returns between 11.18% and 14.30%, corresponding to an outperformance of 3.3 to 6.4 percentage points. The Affinity Propagation approach with Z-Score strategy achieved the highest return of 14.30% with a Sharpe ratio of 6.40. Cointegration approaches, by contrast, reached only 0.81% or showed double-digit losses.

| Ansatz | Strategy | Return (%) | Sharpe Ratio | Max Drawdown (%) |
|--------|----------|------------|--------------|------------------|
| Affinity Propagation | Z-Score | 14.30 | 6.40 | -0.09 |
| Gradient Boost | Z-Score | 13.75 | 6.13 | -0.09 |
| Gradient Boost | Bollinger | 12.11 | 6.95 | -0.09 |
| Affinity Propagation | Bollinger | 11.18 | 6.06 | -0.07 |
| Kointegration | Z-Score | 0.81 | 2.67 | -0.88 |
| Kointegration | Bollinger | -12.57 | 0.10 | -13.09 |

{{< anchor "ftse-rolling" >}}
{{< figure src="/images/la.png" 
           caption="Rolling window analysis of strategy performance on the $F_{100}$ Index with 252-day window. Machine learning approaches significantly outperform traditional methods in European markets as well."
          >}}
{{< anchor "ftse-heatmap" >}}
{{< figure src="/images/1.png" 
           caption="Monthly performance heatmap of the six implemented trading strategies on the $F_{100}$ Index for 2024. Color coding shows positive (green) and negative (red) returns in percent."
          >}}

## Conclusion
The results demonstrate that traditional statistical arbitrage approaches have lost their profitability in the examined markets. Machine learning methods, by contrast, continue to identify profitable arbitrage opportunities while achieving consistent market outperformance with low drawdowns. The monthly performance heatmaps illustrate the different risk profiles: machine learning methods exhibit consistently positive monthly returns, while cointegration-based strategies record frequent negative periods. These results and deeper analyses as well as adjustments to the trading and pair discovery parameters of the respective approaches can be replicated in the [backtester](/setup/). The functionality and setup can be viewed here.
