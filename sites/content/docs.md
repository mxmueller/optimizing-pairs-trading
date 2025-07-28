---
title: "Ausarbeitung"
math: true  # Das aktiviert KaTeX (ist schon im Theme)
toc: true
readTime: true
---

****

Pairs trading is a non-directional trading strategy that works regardless of market direction {{< cite ref="Vidyamurthy 2004" page="p. 8" >}}. It relies on historical relationships between two securities (time series) $X_i(t)$ and $X_j(t)$ and exploits temporary deviations in their price relationship for profit generation. Statistical pairs trading employs two primary methods: cointegration-based and correlation-based techniques. {{< cite ref="Engle 1987" etal="true" noparen="true">}} established the theoretical foundations of cointegration, {{< cite ref="Vidyamurthy 2004" etal="true" noparen="true">}} developed its application in pairs trading, and {{< cite ref="Gatev 2006" etal="true" noparen="true">}} introduced the correlation-based approach. Pairs trading involves two fundamental steps: identifying suitable pairs and trading them.

## The Cointegration Approach
Despite what the name might suggest, cointegration has nothing to do with "integration." According to {{< cite ref="Engle 1987" etal="true" noparen="true">}}, pairs are tested for long-term equilibrium relationships. While time series may deviate from each other in the short term, economic forces theoretically maintain their long-term relationship.

{{< anchor "cointpair" >}}
**Finding Cointegrated Pairs:** To identify such relationships, a regression equation is first estimated:
<a id="f1"></a>
$$X_i(t) = \alpha_{i,j} + \beta_{i,j} X_j(t) + \varepsilon_{i,j}(t)$$

The residuals $\varepsilon_{i,j}(t)$ from this regression must be stationary, even though the original time series $X_i(t)$ and $X_j(t)$ are non-stationary. A stationary process returns to its mean and exhibits constant variance. The Engle-Granger procedure {{< cite ref="Engle 1987" cf="true" >}} tests this stationarity of residuals using the Augmented Dickey-Fuller test {{< cite ref="Dickey 1979" cf="true" >}}. The null hypothesis states that the residuals have a unit root (are non-stationary). If this null hypothesis is rejected at significance level $\alpha_{\text{sig}}$ ($p$-value $< \alpha_{\text{sig}}$), cointegration exists.

**Trading Cointegrated Pairs:** Due to their statistical properties (variance stabilization), prices are applied logarithmically as $\log X_i(t)$ and $\log X_j(t)$. To determine the optimal ratio for a trade, the hedge ratio is established through linear regression:

{{< anchor "f2" >}}
$$\log X_i(t) = \alpha_{i,j} + \beta_{i,j} \log X_j(t) + \varepsilon_{i,j}(t)$$

Where $\alpha_{i,j}$ represents the constant (regression intercept), $\beta_{i,j}$ the hedge ratio (specifying how many units of $X_j$ to trade per unit of $X_i$), and $\varepsilon_{i,j}(t)$ the error term (residuals). The hedge ratio $\beta_{i,j}$ ensures that long and short positions remain market-neutral. Using the hedge ratio, a market-neutral spread can be constructed:

{{< anchor "f3" >}}
$$Spread_{i,j}(t) = \log X_i(t) - \beta_{i,j} \log X_j(t)$$

This spread eliminates common market movements. However, for trading to be profitable, the spread must be mean-reverting:

<a id="f4"></a>
$$Spread_{i,j}(t) = \mu_{i,j} + u_{i,j}(t)$$

where $u_{i,j}(t)$ is a stationary process with $E[u_{i,j}(t)] = 0$. In trading, profitable deviations can only be captured when the spread returns to its mean. To determine when the spread deviates too far from its mean, it is normalized:

{{< anchor "f5" >}}
$$Z_{i,j}(t) = \frac{Spread_{i,j}(t) - \mu_{i,j}}{\sigma_{i,j}}$$

The Z-score enables comparison of deviations and defines clear entry and exit signals. For example, with $\theta = 2$: Long when $Z_{i,j}(t) < -\theta$ by going long $X_i$ and short $\beta_{i,j} \cdot X_j$, or short when $Z_{i,j}(t) > +\theta$ by going short $X_i$ and long $\beta_{i,j} \cdot X_j$. These trades are exited when $Z_{i,j}(t) \rightarrow 0$, as the spread returns to its historical center.

## The Correlation Approach
According to {{< cite ref="Gatev 2006" etal="true" noparen="true">}}, the correlation approach is based on the assumption that $X_i(t)$ and $X_j(t)$ with historically high correlation will continue to exhibit similar price movements in the future. Unlike cointegration-based approaches, this method does not assume long-term equilibrium relationships but rather short-term correlation patterns.

**Finding Correlated Pairs:** In correlation-based methods, pairs are selected according to {{< cite ref="Sharpe 1964" noparen="true">}} using Pearson correlation over a formation period of length $t_f$:

{{< anchor "f6" >}}
$$\rho_{i,j} = \frac{Cov(X_i, X_j)}{\sigma_{X_i} \sigma_{X_j}} = \frac{\sum_{t=1}^{t_f}(X_i(t) - \bar{X_i})(X_j(t) - \bar{X_j})}{\sqrt{\sum_{t=1}^{t_f}(X_i(t) - \bar{X_i})^2}\sqrt{\sum_{t=1}^{t_f}(X_j(t) - \bar{X_j})^2}}$$

where $\bar{X_i}$ and $\bar{X_j}$ represent the means of the respective time series during the formation period. Pairs with $\rho_{i,j} > \rho_{\min}$ above a defined threshold are selected for trading.

**Trading Correlated Pairs:**
For trading pairs according to {{< cite ref="Gatev 2006" etal="true" noparen="true">}}, the time series are first normalized. The cumulative sum[^1] of logarithmic returns is divided by their historical standard deviation:

$$Z_k(t) = \frac{\sum_{s=1}^{t} \log\frac{X_k(s)}{X_k(s-1)}}{\sigma_k} \quad \text{for } k \in \{i,j\}$$

where $\sigma_i$ and $\sigma_j$ are the standard deviations of logarithmic returns during the formation period. The spread between normalized time series is defined as divergence: $D_{i,j}(t) = Z_i(t) - Z_j(t)$. When divergence exceeds a threshold $\delta$, corresponding trading signals are generated. Long $X_i$ and short $X_j$ when $D_{i,j}(t) < -\delta$, and long $X_j$ and short $X_i$ when $D_{i,j}(t) < +\delta$. Positions are closed when divergence converges toward zero ($D_{i,j}(t) \rightarrow 0$).

**** 
## Motivation
**Three key factors** undermine the profitability of static pairs trading applications in today's market environment:

1. **Popularity:** The more market participants use the same strategy, the faster arbitrage opportunities disappear {{< cite ref="Jacobs 2015" cf="true" >}}. The adoption of pairs trading has demonstrably increased among professional traders, institutional investors, and hedge fund managers since the early 2000s {{< cite ref="Miao 2014" page="p. 96" >}}.

2. **Elimination of Inefficiencies:** {{< cite ref="Miao 2014" etal="true" noparen="true" >}} illustrates how High Frequency Trading (HFT) eliminates market inefficiencies through technological advancement. While positions were held for weeks or days during the development of cointegration-based and correlation-based approaches, arbitrage opportunities are now exploited within hours, minutes, or even seconds. The inefficiencies on which classical pairs trading relies are identified and eliminated faster than traditional approaches can respond.

3. **Instability:** {{< cite ref="Chen 2019" etal="true" noparen="true" >}} demonstrate that cointegration relationships between stock pairs are not stable but can fundamentally change or disappear entirely through regime shifts. Market conditions alternate between different states - from cointegrating relationships to Black-Scholes-like markets without statistical arbitrage opportunities.

These challenges reveal specific avenues for advancement. Given the resources of institutional high frequency trading systems, directly improving trading strategies for existing pair discovery methods proves futile in the context of market efficiency. We assume that once an inefficiency exists, various trading strategies can exploit it, but these will always be outpaced by superior resources (computational and transmission speed). When a large proportion of market participants employ documented and historically successful methods like cointegration, correlations, or their derivatives, "crowded trades" emerge that lead to simultaneous liquidations and loss amplification at the first signs of losses. This research therefore hypothesizes that pairs trading profitability and optimization may lie in discovering pairs that remain hidden from these traditional statistical approaches. To address the instability problem, adaptive approaches with rolling windows and dynamic parameters are employed that can continuously adapt to changing market regimes. This leads to the following research question:

> To what extent does a machine learning approach to pair identification improve the performance of pairs trading strategies compared to traditional cointegration-based methods?

As exploratory research, the machine learning approaches are intentionally kept broad. Ultimately, two approaches were developed: an [Affinity Propagation Clustering](#ML1) and [Gradient Boost Regressor](#ML2) method. These are compared with a cointegration-based approach implemented according to {{< cite ref="Engle 1987" etal="true" noparen="true">}}. However, for comparability, this approach also employs the [Sliding Window approach](#Window). Comparative studies justify this selection through validated superiority of cointegration methods over correlation {{< cite ref="Rad 2016">}}; {{< cite ref="Carrasco Blázquez 2018">}}; {{< cite ref="Ma 2022">}}.
****

## Approach

Three distinct pair identification methods are implemented simultaneously (see [Figure 1](#ablauf)): the traditional [cointegration approach](#cointpair) as benchmark and two machine learning methods - [Affinity Propagation Clustering](#ML1) and [Gradient Boost Regressor](#ML2).

Each approach follows its specific pair selection process, with the machine learning methods involving additional feature extraction and model training. Subsequently, the identified pairs undergo statistical validation - both machine learning and cointegration pairs must pass the [Engle-Granger test](#cointpair) with $p < 0.05$. From the validated pairs, the top 20 with the best statistical properties are selected for trading.

![Alt-Text](/images/ablauf.drawio.png "Figure 1: Systematic workflow of pairs trading evaluation with three pair identification approaches, statistical validation, monthly sliding windows, and parallel strategy validation on $N_{100}$ and $F_{100}$ markets.")

The [Sliding Window approach](#Window) shifts both training and trading windows monthly, creating 12 iterative evaluation cycles. Each pair selection is tested with two established trading strategies - [Z-Score](#zscore) and [Bollinger Bands](#bollinger) - on both markets ($N_{100}$ and $F_{100}$) under uniform [market conditions](#MarketSim). This systematic evaluation enables robust performance assessment of all approaches across different market regimes.
****

## Data
To obtain a subset of time series (securities, stocks, or other instruments) for pair formation methods, comparable studies employ pre-selection criteria such as the Global Industry Classification Standard (GICS) {{< cite ref="Do 2010" page="p. 8" >}}.

{{< anchor "economy-chart" >}}
![Alt-Text](/images/economy.drawio.png "Figure 1: Systematic representation of economic structure with classification levels: 1. Global Industry Classification Standard (*GICS*); 2. National sectors (Primary, Secondary, Tertiary sector); 3. Hierarchical industry structure (Industry group; Industry, Sub-industry); 4. Domestic stock indices in the context of global and national economy.")

*GICS* forms the foundation for S&P and MSCI financial market indices, where each firm is assigned to exactly one sub-industry based on its primary business activity, and thus to one industry, industry group, and sector. Potential pairs are then restricted to the sectors or subsectors defined by this classification (see [Figure 1, see 3](#economy-chart)). While this captures economic synergies in pairs, it may wrongly exclude potential connections from the start. To minimize this exclusion, we select stocks at the national economic level (see [Figure 1, see 2](#economy-chart)). We deliberately avoid sector-specific filtering based on the assumption that machine learning methods can identify cross-industry relationships that traditional GICS-based restrictions would miss. In this research, we implement this through the American and British markets using the *NASDAQ-100* and *FTSE-100* (abbreviated as $N_{100}$ and $F_{100}$) (see [Figure 1, see 4](#economy-chart)).

**Indices:** Stock data for both indices spans the period $T = [t_{\text{start}}, t_{\text{end}}]$, where $t_{\text{start}}$ corresponds to January 1, 2020, and $t_{\text{end}}$ to January 1, 2025. This period is divided into training and testing phases: The training period covers $T_{\text{train}} = [01.01.2020, 31.12.2023]$. The testing period spans $T_{\text{test}} = [01.01.2024, 01.01.2025]$. For each stock, a complete dataset is captured on every trading day, including the trading symbol, date, and essential price information: opening price, daily high, daily low, closing price, and trading volume. Since no additional restrictions regarding market capitalization, liquidity, or sector affiliation apply, the pool of all 100 stocks in an index $A = \{a_1, a_2, ..., a_{100}\}$ yields the set of all permissible pairs through $P = \{(a_i, a_j) \mid a_i, a_j \in A \land i < j\}$. This corresponds to $\binom{100}{2} = 4950$ possible pair candidates per index.

{{< anchor "market" >}}
{{< figure src="/images/market_comparison.png" 
           caption="Figure 4: Comparative performance of $F_{100}$ and $N_{100}$ indices from 2020-2025, normalized to base value 100 (January 1, 2020). Gray shaded area indicates the 2024-2025 period. Arrows show total growth rates and 2024-2025 performance."
           width="700" 
           style="text-align: center; margin: 0 auto;" >}}

**Data Cleaning:** Time series without complete data points for the period $T = [t_{\text{start}}, t_{\text{end}}]$ were excluded. This resulted in 94 stocks for $N_{100}$ and 98 stocks for $F_{100}$ per index. For isolated missing values, we use the price time series $X_i(t)$ for each stock $i$. Forward interpolation replaces missing values with the last available value from the same time series: $X_i(t) = X_i(t-k)$, where $k$ is the smallest positive number for which $X_i(t-k)$ was observed. Remaining gaps are then filled with subsequent values: $X_i(t) = X_i(t+m)$, where $m$ is the smallest positive number for which $X_i(t+m)$ was observed. Compared to other methods such as linear or polynomial interpolation, forward and backward interpolation provides a robust solution for financial time series, as it uses only observed values and preserves data continuity {{< cite ref="Moritz 2017" >}}. The cleaned, normalized price progression of all available values per index can be seen in [Figure 2](#market).
****

## Affinity Propagation Clustering 
Affinity Propagation is an exemplar-based clustering method that automatically determines optimal cluster numbers through iterative message passing between data points and selects representative exemplars from the data itself. The algorithm maximizes similarity sums through message exchange that evaluates how well data points serve as cluster centers and how willing others are to accept them {{< cite ref="Dueck 2009" >}}.

This approach was selected for two reasons: First, automatic cluster determination enables flexible cluster number adaptation between time windows in the sliding window procedure. Second, only one documented application for pair discovery in pairs trading exists, but in modified form and in cryptocurrency markets {{< cite ref="Othman 2025" >}}. Using the Silhouette Score, we selected based on the primary features of return and volatility. These are applied in their standard form:

$$\text{Return} = R_i = \frac{1}{T} \sum_{t=1}^{T} \frac{P_t - P_{t-1}}{P_{t-1}} \times \text{Trading days per year}$$
$$\text{Volatility} = V_i = \sqrt{\frac{1}{T-1} \sum_{t=1}^{T} \left( \frac{P_t - P_{t-1}}{P_{t-1}} - \mu \right)^2} \times \sqrt{\text{Trading days per year}}$$

The economic assumption is that stocks with similar risk-return profiles respond comparably to market conditions and therefore exhibit more stable statistical relationships than randomly chosen pairs. Clustering reduces the search space to a few hundred pair combinations within clusters, minimizing the multiple testing problem.

{{< anchor "cluster2" >}}
{{< figure src="/images/cluster1.drawio.png" 
           caption="Figure 3: Affinity Propagation Clustering for $N_{100}$ and $F_{100}$ stocks in return-volatility space with exemplar-based cluster centers and selected pairs after cointegration test and score evaluation in t-SNE similarity space."
          >}}

[Figure 3](#cluster2) shows Affinity Propagation Clustering in the original return-volatility space for the $F_{100}$. The connecting lines illustrate the exemplar-based structure: each stock connects to its cluster center, where the centers are actual stocks from the dataset (not calculated means). A possible economic interpretation of these clusters (important only for the left side of the figure) can be seen using the return-volatility quadrants in [Figure 4](#cluster3).

{{< anchor "cluster3" >}}
{{< figure src="/images/eco.drawio.png" 
           caption="Figure 4: Economic interpretation of return-to-volatility quadrants."
           width="300" 
           style="text-align: center; margin: 0 auto;" >}}

Cointegration tests remain necessary as an additional processing step, since similar return-volatility profiles do not automatically guarantee long-term equilibrium relationships - clustering serves as an economically motivated pre-selection for statistically robust pairs with local significance. Pair selection occurs through a weighted score based on cluster center distance and profile similarity:

{{< anchor "score" >}}
$$S_{i,j} = 0.6 \cdot D_{center,norm} + 0.4 \cdot D_{profile,norm}$$

where $D_{center}$ measures the average euclidean distance of both stocks to cluster center $C$ and $D_{profile}$ measures the direct euclidean distance between stocks in standardized return-volatility space. Both components are min-max normalized and only pairs with [cointegration](#cointpair) $p$-value $< 0.05$ qualify for trading. Final selection results from the top 20 best scores that meet statistical requirements.

[Figure 3](#cluster2) shows on the right side the stocks selected after [score evaluation](#score) and [cointegration test](#cointpair). The t-SNE transformation projects these into a similarity space that better reveals local neighborhoods and exemplarily shows the final pairs of a window.

We avoid configuring the `preference` parameter since cluster numbers should be determined automatically. The $N_{100}$ showed `Silhouette Score` of `0.415`, `Calinski-Harabasz Score` of `93.58`, and `Davies-Bouldin Score` of `0.712` during development. The $F_{100}$ showed `Silhouette Score` of `0.377`, `Calinski-Harabasz Score` of `80.66`, and `Davies-Bouldin Score` of `0.742`.

## Gradient Boost Regressor
The Gradient Boost Regressor combines many weak decision trees into a strong predictive model incrementally, where each new tree uses the residuals (difference between actual and predicted values) of previous trees as target variables. The method systematically analyzes in each iteration which direction predictions need correction to minimize errors, trains a new decision tree that learns exactly these corrections, and adds it to the overall prediction {{< cite ref="He 2019" >}}.

At the time of writing, no comparable application for pair discovery exists in the literature. Studies such as {{< cite ref="Krauss 2017" etal="true" cf="true" noparen="true" >}} titled *"Deep neural networks, gradient-boosted trees, random forests: Statistical arbitrage on the S&P 500"* show that Gradient-Boosted Trees outperform both Deep Neural Networks (0.33%) and Random Forests (0.43%) in statistical arbitrage strategies with 0.37% daily returns before transaction costs. This demonstrates the method's potential for successful application in pairs trading.

The regressor uses a multidimensional feature vector to predict average spread deviations between stock pairs. This target variable selection follows validation as a target variable in related machine learning works connected to statistical arbitrage {{< cite ref="Sarmento 2020" >}}; {{< cite ref="Lin 2021" >}}. Empirical findings show that price differences between cointegrated stocks in classical pairs trading do not converge but persist, causing losses. Traditional methods measure spreads, define thresholds, and react accordingly. Machine learning approaches, however, forecast stock pairs with future minimal spread volatility. Instead of trading all cointegrated pairs and awaiting their convergence, the model selects only pairs with predicted spread stability.

The final feature matrix comprises 32 dimensions: 3 statistical base features, 20 technical time series indicators, 6 volume properties, and 3 extended MACD components. Missing values are handled through SimpleImputer with mean strategy:

| Feature | Description |
|:------------------|:-------------|
| **`Correlation`** | Uses the previously introduced [Pearson correlation](#f6) from the correlation approach, but not as a selection criterion with fixed threshold $ρ_{min}$, rather as a continuous feature. |
| **`Beta`** | Sensitivity ratio: $R_{i,t} = α + β_{i,j} · R_{j,t} + ε_t$ from regression. |
| **`Residual Standard Deviation`** | The precision of this linear relationship. |
| **`Rate of Change`** | Percentage price changes over 5, 20, and 50 days for both stocks and their differences. |
| **`Williams Oscillators`** | Relative position of current prices over 10, 14, 28, and 40 days for both stocks and their differences. |
| **`Bollinger Bands`** | Spread volatility relative to moving average for 5, 10, 20, 25, and 50 days. |
| **`Moving Average Convergence/Divergence`** | Trend momentum with parameter sets (12,26,9) and (5,13,5). Captures line differences, signal line differences, and binary crossover signals for both stocks. |
| **`Volume Rate of Change`** | Momentum indicators over 5, 20, and 50 days for both stocks and their differences. |
| **`Volume Averages and Standard Deviations`** | Moving averages and dispersion measures for 50 and 100 days. |
| **`Volume Changes`** | Percentage changes for 50 and 100 days. |

Feature selection and time window choices resulted from a two-stage optimization process. A feature set of 80 technical indicators with varying time windows was evaluated using `Gradient Boosting Feature Importance Analysis`. From the initial feature importance ranking, the 32 strongest features were selected while eliminating redundant features with high correlation.

The final model's hyperparameters include `learning_rate` of `0.2`, `max_depth` of `2`, and `n_estimators` of `300` trees, plus `min_samples_split` and `min_samples_leaf` of `2` each. Parameter selection occurred through grid search with `learning_rate` $∈ {0.01, 0.1, 0.2}$, `max_depth` $∈ {2, 3, 4}$, `n_estimators` $∈ {100, 200, 300}$, and regularization parameters `min_samples_split` $∈ {2, 4}$ and `min_samples_leaf` $∈ {1, 2}$. Five-fold cross-validation with $R²$-Score as optimization metric yielded the final configuration. Training occurs on 80% of available data with 20% test set evaluation.

{{< anchor "regressor" >}}
{{< figure src="/images/regressorv1.drawio.png" 
           caption="Figure 5: Predicted vs Actual representation of Gradient Boosting models for $N_{100}$ (left) and $F_{100}$ (right). The linear relationship between predicted and actual spread deviations confirms the predictive quality of both models."
           style="text-align: center; margin: 0 auto;" >}}

In the final step, pairs are also statistically tested with [cointegration](#cointpair) $p$-value $< 0.05$ and selected in descending order by top 20 based on their mean-reversion properties for trading.

The Predicted vs Actual representations in [Figure 5](#regressor) confirm solid predictive performance of both models. The $N_{100}$ model achieves an `R²` of `0.707` with `MSE` of `0.068` and `MAE` of `0.201`, while the $F_{100}$ model achieves an `R²` of `0.652` with `MSE` of `0.084` and `MAE` of `0.227`.

## Sliding Windows 
The Sliding Window approach applied in this research shifts both the training and trading windows. For each iteration $i \in \{1, 2, ..., 12\}$, both time periods are shifted synchronously by $\Delta t = 1$ month. The training and trading windows are defined as:

$$T_{train}^{(i)} = [t_{start} + (i-1) \cdot \Delta t, t_{train\_end} + (i-1) \cdot \Delta t]$$
$$T_{trade}^{(i)} = [t_{train\_end} + (i-1) \cdot \Delta t + 1, t_{train\_end} + (i-1) \cdot \Delta t + \Delta_{trade}]$$

with $t_{train\_end} = 01.01.2024$ and $\Delta_{trade} = 1$ month. This coupled shift ensures that the training window maintains its 3-year length, as visualized in [Figure 6](#window).

{{< anchor "window" >}}
{{< figure src="/images/window.drawio.png" 
           caption="Figure 6: Coupled shift of both windows across 12 iterations."
          >}}

The temporal assignment between pair identification and trade execution follows a strict rule: Stock pairs identified in training window $T_{train}^{(i)}$ may only be opened in the directly following trading window $T_{trade}^{(i)}$. However, already opened trades can be closed in later windows $T_{trade}^{(j)}$ with $j > i$, as long as the exit conditions are met.

## Trading Strategies 
To evaluate the identified pairs, two established technical trading strategies are applied: a **Z-Score** and a **Bollinger-Band** based strategy. Z-Score has become a widely used method in pairs trading {{< cite ref="Quantinsti 2025" >}}, as pairs trading ranks among the most frequently used market-neutral strategies {{< cite ref="Carrasco Blázquez 2018" >}}. Bollinger Bands are implemented as an additional strategy because, unlike the fixed thresholds of Z-Score, they use dynamic bands that adapt to market volatility {{< cite ref="Leung 2020" >}}; {{< cite ref="Syril 2025" >}}.

{{< anchor "window" >}}
{{< figure src="/images/strategies.drawio.png" 
           caption="Figure 6: Coupled shift of both windows across 12 iterations."
           width="800" 
          >}}

### Z-Score Strategy

The Z-Score strategy uses the previously introduced [Z-Score normalization](#f5) with rolling windows of $w_2 = 60$ trading days for calculating $\mu_{i,j}$ and $\sigma_{i,j}$. This threshold applies to the evaluation and was selected as the mean value (but can be adjusted). According to {{< cite ref="Krauss 2015" etal="true" cf="true" noparen="true">}} from the Institute for Economics at the University of Erlangen-Nuremberg, typical window sizes for historical means and standard deviations in pairs trading strategies range between 30 and 90 days.
 
| Signal | Condition |
|--------|-----------|
| Long | $Z_{i,j}(t) < -2.0$ → Long $X_i$, Short $\beta_{i,j} \cdot X_j$ |
| Short | $Z_{i,j}(t) > +2.0$ → Short $X_i$, Long $\beta_{i,j} \cdot X_j$ |
| Exit | $\|Z_{i,j}(t)\| < 0.5$ |

### Bollinger Bands Strategy
The Bollinger Band strategy differs from the Z-Score implementation in three key aspects. The hedge ratio is re-estimated every $r = 3$ trading days based on the last $w_{hr} = 25$ observations:
$$\beta_{i,j}(t) = \arg\min_{\beta} \sum_{k=t-25+1}^{t} [X_i(k) - \beta \cdot X_j(k)]^2$$

Here $\arg\min$ denotes the β-value that minimizes the sum of squared residuals (OLS regression), and $t-25+1$ to $t$ encompasses the last 25 trading days including the current time point. Using short rolling windows for hedge ratio estimation is established in quantitative finance literature {{< cite ref="QuantStart 2020" >}} and enables faster strategy adaptation to changing market conditions {{< cite ref="Feng 2023" >}}. For the absolute price-based spread, unlike the logarithmic [spread construction](#f3), we use:

$$Spread_{i,j}(t) = X_i(t) - \beta_{i,j}(t) \cdot X_j(t)$$

The adaptive bands are applied with a rolling window of $w = 20$ trading days:

$$Upper_{i,j}(t) = \mu_{spread}(t) + 2.0 \cdot \sigma_{spread}(t)$$
$$Lower_{i,j}(t) = \mu_{spread}(t) - 2.0 \cdot \sigma_{spread}(t)$$

The bands define dynamic entry and exit thresholds that automatically adapt to changing volatility conditions. Positions are opened when bands are breached and closed when converging to the mean.

| Signal | Condition |
|--------|-----------|
| Long | $Spread_{i,j}(t) < Lower_{i,j}(t)$ |
| Short | $Spread_{i,j}(t) > Upper_{i,j}(t)$ |
| Exit | $\|Spread_{i,j}(t) - \mu_{spread}(t)\| < 0.5 \cdot \sigma_{spread}(t)$ |

## Market Simulation 
All pairs are tested under uniform market conditions. Starting capital amounts to €100,000 with a fixed position size of 1% of available capital per trade. Realistic transaction costs are simulated through a fixed commission of €1.00 per trade plus a variable fee of 0.018% of trading volume. Additionally, a bid-ask spread of 0.1% is considered, applying to both entry and exit. This cost structure corresponds to typical retail brokerage conditions and ensures realistic performance evaluation {{< cite ref="Interactive Brokers 2024" >}}. The risk-free interest rate is set at 0% since opportunity costs are minimized by the market-neutral nature of pairs trading. The results are summarized on the [following page](/results/).

## Literatur
{{< reference "Sharpe 1964" >}}Sharpe, W. F. (1964). Capital Asset Prices: A Theory of Market Equilibrium Under Conditions of Risk. The Journal of Finance, 19(3), 425-442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x{{< /reference >}}

{{< reference "Dickey 1979" >}}Dickey, D. A., & Fuller, W. A. (1979). Distribution of the Estimators for Autoregressive Time Series with a Unit Root. Journal of the American Statistical Association, 74, 427-431. https://api.semanticscholar.org/CorpusID:56458593{{< /reference >}}

{{< reference "Engle 1987" >}}Engle, R. F., & Granger, C. W. J. (1987). Co-integration and Error Correction: Representation, Estimation, and Testing. Econometrica, 55(2), 251-276. https://ideas.repec.org/a/ecm/emetrp/v55y1987i2p251-76.html{{< /reference >}}

{{< reference "Vidyamurthy 2004" >}}Vidyamurthy, G. (2004). Pairs Trading: Quantitative Methods and Analysis. John Wiley & Sons, Hoboken, New Jersey.{{< /reference >}}

{{< reference "Gatev 2006" >}}Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). Pairs Trading: Performance of a Relative Value Arbitrage Rule. Yale ICF Working Paper No. 08-03. https://doi.org/10.2139/ssrn.141615{{< /reference >}}

{{< reference "Dueck 2009" >}}Dueck, D. (2009). Affinity propagation: Clustering data by passing messages. PhD thesis.{{< /reference >}}

{{< reference "Do 2010" >}}Do, B., & Faff, R. (2010). Does simple pairs trading still work? Financial Analysts Journal, 66(4), 83-95. https://doi.org/10.2469/faj.v66.n4.1{{< /reference >}}

{{< reference "Miao 2014" >}}Miao, G. J. (2014). High frequency and dynamic pairs trading based on statistical arbitrage using a two-stage correlation and cointegration approach. International Journal of Economics and Finance, 6, 96. https://api.semanticscholar.org/CorpusID:54175142{{< /reference >}}

{{< reference "Krauss 2015" >}}Krauss, C. (2015). Statistical arbitrage pairs trading strategies: Review and outlook. IWQW Discussion Papers, No. 09/2015, Friedrich-Alexander-Universität Erlangen-Nürnberg, Institut für Wirtschaftspolitik und Quantitative Wirtschaftsforschung (IWQW), Nürnberg. https://hdl.handle.net/10419/116783{{< /reference >}}

{{< reference "Jacobs 2015" >}}Jacobs, H., & Weber, M. (2015). On the determinants of pairs trading profitability. Journal of Financial Markets, 23, 75-97. https://doi.org/10.1016/j.finmar.2014.12.001{{< /reference >}}

{{< reference "Rad 2016" >}}Rad, H., Low, R. K. Y., & Faff, R. (2016). The profitability of pairs trading strategies: distance, cointegration and copula methods. Quantitative Finance, 16(10), 1541-1558. https://doi.org/10.1080/14697688.2016.1164337{{< /reference >}}

{{< reference "Moritz 2017" >}}Moritz, S., & Bartz-Beielstein, T. (2017). imputeTS: Time series missing value imputation in R. The R Journal, 9(1), 207-218. https://doi.org/10.32614/RJ-2017-009{{< /reference >}}

{{< reference "Krauss 2017" >}}Krauss, C., Do, X. A., & Huck, N. (2017). Deep neural networks, gradient-boosted trees, random forests: Statistical arbitrage on the S&P 500. European Journal of Operational Research, 259(2), 689-702. https://doi.org/10.1016/j.ejor.2016.10.031{{< /reference >}}

{{< reference "Carrasco Blázquez 2018" >}}Carrasco Blázquez, M., De la Orden De la Cruz, C., & Prado Román, C. (2018). Pairs trading techniques: An empirical contrast. European Research on Management and Business Economics, 24(3), 160-167. https://doi.org/10.1016/j.iedeen.2018.05.002{{< /reference >}}

{{< reference "He 2019" >}}He, Z., Lin, D., Lau, T., & Wu, M. (2019). Gradient boosting machine: A survey. arXiv preprint arXiv:1908.06951. https://arxiv.org/abs/1908.06951{{< /reference >}}

{{< reference "Chen 2019" >}}Chen, K., Chiu, M. C., & Wong, H. Y. (2019). Time-consistent mean-variance pairs-trading under regime-switching cointegration. SIAM Journal on Financial Mathematics, 10(2), 632-665. https://doi.org/10.1137/18M1209611{{< /reference >}}

{{< reference "QuantStart 2020" >}}QuantStart. (2020). Dynamic Hedge Ratio Between ETF Pairs Using the Kalman Filter. Retrieved from https://www.quantstart.com/articles/Dynamic-Hedge-Ratio-Between-ETF-Pairs-Using-the-Kalman-Filter/ {{< /reference >}}

{{< reference "Leung 2020" >}}Leung, J. M. J., & Chong, T. T. L. (2020). The profitability of Bollinger Bands: Evidence from the constituent stocks of Taiwan 50. Physica A: Statistical Mechanics and its Applications, 539, 122949.{{< /reference >}}

{{< reference "Sarmento 2020" >}}Sarmento, S. M., & Horta, N. (2020). Enhancing a pairs trading strategy with the application of machine learning. Expert Systems with Applications, 158, 113490. https://doi.org/10.1016/j.eswa.2020.113490{{< /reference >}}

{{< reference "Lin 2021" >}}Lin, T.-Y., Chen, C. W. S., & Syu, F.-Y. (2021). Multi-asset pair-trading strategy: A statistical learning approach. The North American Journal of Economics and Finance, 55, 101295. https://doi.org/10.1016/j.najef.2020.101295{{< /reference >}}

{{< reference "Ma 2022" >}}Ma, B., & Ślepaczuk, R. (2022). The profitability of pairs trading strategies on Hong-Kong stock market: distance, cointegration, and correlation methods. Working Papers 2022-02, Faculty of Economic Sciences, University of Warsaw. https://ideas.repec.org/p/war/wpaper/2022-02.html{{< /reference >}}

{{< reference "Feng 2023" >}}Feng, Y., Zhang, Y., & Wang, Y. (2023). Out‐of‐sample volatility prediction: Rolling window, expanding window, or both? Journal of Forecasting, 43, 567-582. https://doi.org/10.1002/for.3046{{< /reference >}}

{{< reference "Interactive Brokers 2024" >}}Interactive Brokers LLC. (2024). Commission Schedule and Trading Costs. Retrieved from https://www.interactivebrokers.com/en/pricing/commissions-stocks{{< /reference >}}

{{< reference "Quantinsti 2025" >}}QuantInsti. (2025). Pairs Trading for Beginners: Correlation, Cointegration, Examples, and Strategy Steps. Retrieved from https://blog.quantinsti.com/pairs-trading-basics/{{< /reference >}}

{{< reference "Othman 2025" >}}Othman, A. H. A. (2025). Enhancing pairs trading strategies in the cryptocurrency industry using machine learning clustering algorithms. London Journal of Research In Management & Business, 25(1), 33-52. https://journalspress.uk/index.php/LJRMB/article/view/1179{{< /reference >}}

{{< reference "Syril 2025" >}}Syril, W. M., & Nagarajan, C. D. (2025). Optimizing commodity futures trading in the financial market: Fine-tuning Bollinger Bands strategy. Global Business Review. https://doi.org/10.1177/09721509251328555{{< /reference >}}

