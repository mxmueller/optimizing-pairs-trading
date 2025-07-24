---
title: "Results"
math: true  # Das aktiviert KaTeX (ist schon im Theme)
readTime: true
---

Die nachfolgende Auswertung der Ergebnisse Hypothese: *Machine Learning-basierte Ansätze zur Paaridentifikation übertreffen traditionelle kointegrationsbasierte Verfahren im Pairs Trading.* Die durch Machine Learning Ansätze gefundenen Paare schlagen im Gegensatz zu den kointegrationsbasierten Verfahren mit ihren jeweiligen Strategien den Markt ($F_{100}$: +7,9%, $N_{100}$: +15,8% für das Jahr 2024).

## Performance am $N_{100}$-Index

Am $N_{100}$ erreichte der Gradient Boost Regressor 20,90% Jahresrendite (Z-Score) bei einer Sharpe Ratio von 6,16. Dies entspricht einer Marktoutperformance von 5,1 Prozentpunkten gegenüber dem $N_{100}$ Index. Der Affinity Propagation Ansatz erzielte 17,98% mit einer Sharpe Ratio von 7,48. Die traditionellen Kointegrationsansätze erreichten dagegen -1,13% oder wiesen zweistellige Verluste auf.

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
           caption="Rolling-Window-Analyse der Strategieperformance am $N_{100}$-Index mit 252-Tage-Fenster. Machine Learning-Verfahren zeigen konsistent positive Performance, während Kointegrationsansätze volatil verlaufen."
          >}}

{{< anchor "nasdaq-heatmap" >}}
{{< figure src="/images/2.png" 
           caption="Monatliche Performance-Heatmap der sechs Trading-Strategien am $N_{100}$-Index für 2024. Die Darstellung verdeutlicht die unterschiedliche Marktanpassung der Algorithmen. Farbskala von rot (Underperformance) bis grün (Outperformance)."
          >}}

## Performance am $F_{100}$-Index

Am $F_{100}$ generierten beide Machine-Learning-Verfahren Renditen zwischen 11,18% und 14,30%, was einer Outperformance von 3,3 bis 6,4 Prozentpunkten entspricht. Der Affinity Propagation Ansatz mit Z-Score Strategie erreichte die höchste Rendite von 14,30% bei einer Sharpe Ratio von 6,40. Die Kointegrationsansätze erreichten dagegen nur 0,81% oder wiesen zweistellige Verluste auf.

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
           caption="Rolling-Window-Analyse der Strategieperformance am $F_{100}$-Index mit 252-Tage-Fenster. Auch am europäischen Markt übertreffen Machine Learning-Ansätze die traditionellen Verfahren deutlich."
          >}}

{{< anchor "ftse-heatmap" >}}
{{< figure src="/images/1.png" 
           caption="Monatliche Performance-Heatmap der sechs implementierten Trading-Strategien am $F_{100}$-Index für das Jahr 2024. Die Farbcodierung zeigt positive (grün) und negative (rot) Renditen in Prozent an."
          >}}

## Fazit

Die Ergebnisse zeigen, dass traditionelle statistische Arbitrage-Ansätze in den untersuchten Märkten ihre Profitabilität verloren haben. Die Machine-Learning-Verfahren identifizieren dagegen weiterhin profitable Arbitragemöglichkeiten und erreichen dabei eine konsistente Marktoutperformance bei niedrigen Drawdowns. Die monatlichen Performance-Heatmaps verdeutlichen die unterschiedlichen Risikoprofile: Machine-Learning-Verfahren weisen konsistent positive monatliche Erträge auf, während kointegrationsbasierte Strategien häufige negative Perioden verzeichnen.

Diese Ergebnisse und tiefergehende Analysen sowie Anpassungen der Handels- und Paarfindungsparameter der jeweiligen Ansätze können im Backtester nachgestellt werden. Die Funktionsweise und das Setup können hier gesehen werden.