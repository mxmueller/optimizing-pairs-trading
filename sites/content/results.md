---
title: "Results"
math: true  # Das aktiviert KaTeX (ist schon im Theme)
readTime: true
---


Die nachfolgende Auswertung der Ergebnisse Hypothese: *Machine Learning-basierte Ansätze zur Paaridentifikation übertreffen traditionelle kointegrationsbasierte Verfahren im Pairs Trading.* Die durch Maschine Learning Ansätze gefunden Paare schlagen im gegensatz zu den Konitegrierten verfahren in mit ihren jeweiligen Strategien den Markt ($F_{100}$: +7,9%, $N_{100}$: +15,8% für das Jahr 2024). Die nachfolgende Tabelle zeigt die vollständigen Performance-Kennzahlen aller sechs implementierten Strategien, sortiert nach Gesamtrendite:

| Markt | Ansatz | Strategy | Return (%) | Sharpe Ratio | Max Drawdown (%) |
|-------|--------|----------|------------|--------------|------------------|
| $N_{100}$ | Gradient Boost | Z-Score | 20.90 | 6.16 | -0.11 |
| $N_{100}$ | Gradient Boost | Bollinger | 20.47 | 6.73 | -0.18 |
| $N_{100}$ | Affinity Propagation | Z-Score | 17.98 | 7.48 | -0.09 |
| $N_{100}$ | Affinity Propagation | Bollinger | 13.53 | 7.01 | -0.05 |
| $N_{100}$ | Kointegration | Z-Score | -1.13 | 1.03 | -3.87 |
| $N_{100}$ | Kointegration | Bollinger | -11.21 | 0.63 | -11.99 |
| $F_{100}$ | Affinity Propagation | Z-Score | 14.30 | 6.40 | -0.09 |
| $F_{100}$ | Gradient Boost | Z-Score | 13.75 | 6.13 | -0.09 |
| $F_{100}$ | Gradient Boost | Bollinger | 12.11 | 6.95 | -0.09 |
| $F_{100}$ | Affinity Propagation | Bollinger | 11.18 | 6.06 | -0.07 |
| $F_{100}$ | Kointegration | Z-Score | 0.81 | 2.67 | -0.88 |
| $F_{100}$ | Kointegration | Bollinger | -12.57 | 0.10 | -13.09 |

Am $N_{100}$ erreichte der Gradient Boost Regressor 20,90% Jahresrendite (Z-Score) bei einer Sharpe Ratio von 6,16. Dies entspricht einer Marktoutperformance von 5,1 Prozentpunkten gegenüber dem $N_{100}$ Index. Der Affinity Propagation Ansatz erzielte 17,98% mit einer Sharpe Ratio von 7,48. Am $F_{100}$ generierten beide Maschine-Learning-Verfahren Renditen zwischen 11,18% und 14,30%, was einer Outperformance von 3,3 bis 6,4 Prozentpunkten entspricht. 

{{< anchor "window" >}}
{{< figure src="/images/rolling.png" 
           caption="Rolling-Window-Analyse der Strategieperformance mit 252-Tage-Fenster (entspricht einem Handelsjahr). Jeder Datenpunkt repräsentiert die kumulative Rendite der vorangegangenen 252 Handelstage, wodurch kurzfristige Volatilität geglättet und langfristige Trends sichtbar werden."
          >}}

Die traditionellen Kointegrationsansätze erreichten dagegen 0,81% (FTSE) bzw. -1,13% (NASDAQ) oder wiesen zweistellige Verluste auf. Die monatlichen Performance-Heatmaps zeigen die unterschiedlichen Risikoprofile der Ansätze. Die Maschine-Learning-Verfahren weisen konsistent positive monatliche Erträge auf, während die kointegrationsbasierten Strategien häufige negative Perioden verzeichnen.

{{< anchor "window" >}}
{{< figure src="/images/1.png" 
           caption="Monatliche Performance-Heatmap der sechs implementierten Trading-Strategien am $F_{100}$-Index für das Jahr 2024. Die Farbcodierung zeigt positive (grün) und negative (rot) Renditen in Prozent an. Werte repräsentieren die Differenz zwischen Monatsanfang und -ende der kumulativen Performance."
          >}}

{{< anchor "window" >}}
{{< figure src="/images/2.png" 
           caption="Monatliche Performance-Heatmap der sechs Trading-Strategien am $N_{100}$-Index für 2024. Die Darstellung verdeutlicht die unterschiedliche Marktanpassung der Algorithmen zwischen amerikanischem und europäischem Aktienmarkt. Farbskala von rot (Underperformance) bis grün (Outperformance)."
          >}}

Die Ergebnisse zeigen, dass traditionelle statistische Arbitrage-Ansätze in den untersuchten Märkten ihre Profitabilität verloren haben. Die Maschine-Learning-Verfahren identifizieren dagegen weiterhin profitable Arbitragemöglichkeiten und erreichen dabei eine konsistente Marktoutperformance bei niedrigen Drawdowns. Diese Ergebnisse und tiefergehende Analysen sowie anpassungen der Handels und Paarfindungsparamter der jeweiligen Ansäzte können im Backtester nachgestellt werden. Die Funktionsweise und das Setup können hier gesehen werden. 