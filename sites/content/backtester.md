---
title: "Backtester"
math: true  # Das aktiviert KaTeX (ist schon im Theme)
toc: true
readTime: true

---


## Konfiguration Sidebar

Die Konfiguration Sidebar ist der zentrale Steuerbereich der Backtesting-Anwendung. Alle Analysen basieren auf diesen Einstellungen.

{{< anchor "window" >}}
{{< figure src="/images/gif/config.gif" 
          >}}

### Markt & Strategie

Wählen Sie zunächst einen Markt aus dem `Select Market` Dropdown. Dies bestimmt, welche Aktien und Strategien verfügbar sind. Nach der Marktauswahl erscheinen im `Select Strategy` Dropdown nur kompatible Strategien. Ohne gültige Auswahl zeigt die Anwendung "No strategies available for selected market".

### Parameter & Kosten

Die **Trading Parameters** umfassen das **Initial Capital** (Startkapital für die Simulation, Standard: `$100,000`, Mindestbetrag `$1,000`) und die **Position Size** als Prozentsatz des Kapitals pro Position (Standard: `1.0%`, Bereich: `0.1%` bis `10.0%`). Die Position Size kontrolliert das Risiko und die Anzahl gleichzeitiger Positionen.

Der erweiterbarer Bereich **Trading Costs** enthält vier wichtige Kostenparameter: **Fixed Commission** (`$1.00` Standard) als feste Gebühr pro Trade, **Variable Fee** (`0.018%` Standard) als prozentuale Gebühr auf den Handelswert, **Bid-Ask Spread** (`0.1%` Standard) für die Geld-Brief-Spanne und **Risk-Free Rate** (`0.0%` Standard) als risikoloser Zinssatz für die Sharpe Ratio Berechnung.

Alle Parameter werden sofort in allen Analyse-Tabs übernommen. Die Tabs sind erst nach Auswahl von Markt und Strategie zugänglich.

****

## Market Overview

Der Market Overview Tab bietet einen schnellen Überblick über den gewählten Markt und ermöglicht den Vergleich einzelner Aktien.

{{< anchor "window" >}}
{{< figure src="/images/gif/overview.gif" 
          >}}

### Market Index

Die linke Seite zeigt den **Market Index** als Zeitreihen-Chart mit der aktuellen Indexbewertung und der absoluten Veränderung seit Beginn. Die **Current** Metrik zeigt den aktuellen Indexwert, während die grüne/rote Zahl die Gesamtveränderung anzeigt. Der Chart visualisiert die historische Entwicklung des Marktindex über den verfügbaren Zeitraum.

Darunter befindet sich die **Symbol Comparison** Sektion. Wählen Sie bis zu 5 Aktien aus dem `Compare symbols` Multiselect aus, um deren Kursentwicklung zu vergleichen. Der resultierende Linien-Chart zeigt die Schlusskurse aller ausgewählten Symbole über die Zeit, mit unterschiedlichen Farben für jede Aktie.

### Symbol Liste

Die rechte Spalte enthält die **Symbols** Liste mit allen verfügbaren Aktien des gewählten Marktes. Die Anzeige `Total: X` gibt die Gesamtanzahl der Symbole an. Die scrollbare Tabelle zeigt alle Symbole alphabetisch sortiert und dient als Referenz für die verfügbaren Aktien im Markt.

Alle Daten basieren auf dem in der Configuration Sidebar gewählten Markt und aktualisieren sich automatisch bei Marktänderungen.

****

## Symbol Analysis

Der Symbol Analysis Tab vergleicht die Handelsstrategie mit einer Buy & Hold Strategie für einzelne Aktien und zeigt detaillierte Trade-Informationen.

{{< anchor "window" >}}
{{< figure src="/images/gif/symbol.gif" 
          >}}

### Chart-Analyse

Wählen Sie eine Aktie aus dem `Select Symbol` Dropdown. Der obere Chart zeigt drei Linien: die **Price History** (goldene Linie) mit dem historischen Kursverlauf, die **Buy & Hold Return** (grüne Linie) als prozentuale Rendite einer einfachen Kaufen-und-Halten-Strategie, und die **Trading Strategy Return** (magenta Linie) als kumulative Rendite der gewählten Handelsstrategie.

Der untere Chart visualisiert einzelne Trades mit **Profitable Trades** (blaue Punkte) und **Losing Trades** (rote Punkte). Jeder Punkt repräsentiert einen Trade mit seiner individuellen Rendite. Eine gestrichelte graue Linie bei 0% trennt profitable von verlustbringenden Trades.

### Trade-Details & Performance

Unterhalb der Charts befindet sich die vollständige **All Trades** Tabelle mit allen ausgeführten Trades, sortierbar nach Datum, Entry/Exit-Preisen, Performance und Trade-Typ. Die Tabelle zeigt `entry_date`, `exit_date`, `position_type`, `entry_price`, `exit_price`, `performance` und `exit_type`.

Die **Symbol Trades** Sektion zeigt grundlegende Metriken wie `Total Trades` und `Win Rate`. Daneben werden detaillierte Performance-Kennzahlen angezeigt: `Total Performance`, `Avg Performance`, `Max Gain` und `Max Loss` der ausgewählten Aktie basierend auf den konfigurierten Trading-Parametern.

## Strategy Performance

Der Strategy Performance Tab analysiert die Gesamtperformance der gewählten Handelsstrategie mit detaillierten Zeitreihen und Kennzahlen.

{{< anchor "window" >}}
{{< figure src="/images/gif/performance.gif" 
          >}}

### Performance Over Time

Die linke Seite zeigt die **Portfolio Equity Curve** als Hauptchart mit der Entwicklung des Gesamtkapitals über die Zeit. Die blaue Linie stellt das `Total Capital` dar, während eine gestrichelte rote Linie das `Initial Capital` markiert. Unterhalb befindet sich der **Daily Profit/Loss** Chart als Balkendiagramm, wobei grüne Balken profitable Tage und rote Balken Verlusttage darstellen.

Drei Metriken fassen die wichtigsten Ergebnisse zusammen: `Cumulative P&L` als absoluter Gewinn/Verlust, `Net P&L (after costs)` nach Abzug aller Handelskosten, und `Total Return` als prozentuale Gesamtrendite. Der **Active Positions Over Time** Chart zeigt zusätzlich die Anzahl gleichzeitiger Positionen über den Handelszeitraum.

### Performance Metrics

Die rechte Spalte enthält wichtige Kennzahlen wie `Total Trades`, `Final Capital` mit prozentualer Veränderung, `Win Rate`, `Profitable Days`, `Sharpe Ratio` und `Max Drawdown`. 

Drei Tabs strukturieren die detaillierten Metriken: **Performance** zeigt `Total Performance`, `Avg Performance`, `Max Gain/Loss` und Trade-Statistiken. **Costs** listet `Total Costs`, `Avg Cost per Trade` und eine Aufschlüsselung nach Entry/Exit-Kosten (Commission, Variable Fee, Spread). **Portfolio** zeigt Kapital-Kennzahlen wie `Initial/Final/Max/Min Capital` sowie `Current Invested` und `Current Available`.

****

## Pairs Analysis

Der Pairs Analysis Tab analysiert Pair-Trading-Strategien für ausgewählte Aktienpaare innerhalb spezifischer Trading-Windows.

{{< anchor "window" >}}
{{< figure src="/images/gif/pair.gif" 
          >}}

### Symbol-Auswahl & Trades

Wählen Sie zunächst ein **Trading Window** aus dem Dropdown - dies bestimmt den Analysezeitraum. Anschließend wählen Sie in der zweispaltigen Auswahl das **erste Symbol** (links) und das **zweite Symbol** (rechts). Die Dropdowns zeigen nur Aktien, die tatsächlich in diesem Window gehandelt wurden.

Die **Trades Visualization** zeigt eine Statistik-Zeile mit `Total Trades`, `Profit Trades`, `Loss Trades` und `Break-Even` Trades für das gewählte Paar. Darunter befinden sich **Display Options** zum Wechseln zwischen "Active Trade Periods Only" und "All Data". Die Timeline-Charts für beide Symbole visualisieren Entry-Punkte (blaue Dreiecke), Exit-Punkte (farbige Kreise je nach Ergebnis) und Verbindungslinien zwischen Entry/Exit. Die **Trades Details** Tabelle listet alle Pair-Trades mit Datum, Preisen, Performance und Trade-Typ.

### Pairs Overview

Die **Pairs Overview** Sektion zeigt eine Metriken-Zeile mit `Window`, `Total Pairs`, `Total Trades` und `Selected Pair` Information. Der **Top 20 Pairs** Balken-Chart visualisiert die aktivsten Paare nach Anzahl Trades, farbkodiert nach Handelsvolumen. Die vollständige Pairs-Tabelle darunter listet alle verfügbaren Paare des Windows sortiert nach Trade-Anzahl, mit den Spalten `Pair`, `Symbol 1`, `Symbol 2` und `Trades`.

****

## Strategy Comparison

Der Strategy Comparison Tab vergleicht mehrere Handelsstrategien direkt miteinander und bietet umfassende Export-Funktionen für statistische Analysen.

{{< anchor "window" >}}
{{< figure src="/images/gif/last.gif" 
          >}}

### Performance Metrics

Wählen Sie mindestens 2 Strategien aus dem `Select Strategies to Compare` Multiselect. Die Vergleichstabelle zeigt `Total Return`, `Sharpe Ratio`, `Max Drawdown`, `Win Rate`, `Total Trades` und `Profitable Days` für alle gewählten Strategien. Darunter werden separate Balken-Charts für jeden Kennwert angezeigt, um direkte Vergleiche zu visualisieren.

### Equity Curves & Returns

Der **Equity Curves** Tab visualisiert die Kapitalentwicklung aller Strategien in einem gemeinsamen Chart mit verschiedenen Farben pro Strategie und einer gestrichelten Linie für das Initial Capital.

**Returns Distribution** zeigt Histogramme der täglichen Renditen aller Strategien überlagert und eine Statistik-Tabelle mit `Mean Return`, `Std Dev`, `Min/Max Return` und `Positive Days` für jede Strategie.

### Drawdowns Analysis

Zeitreihen-Chart aller Drawdowns mit umgekehrter Y-Achse (tiefere Drawdowns weiter unten) und ein Balken-Chart der maximalen Drawdowns pro Strategie. Drawdowns werden als negative Prozentpunkte dargestellt.

### Pair Analysis

Nach Trading Window-Auswahl zeigt eine Tabelle alle Paare mit Trade-Anzahlen pro Strategie. **Common Pairs** listet Paare auf, die in allen Strategien vorkommen. Für ausgewählte Common Pairs werden detaillierte Performance-Vergleiche mit `Total Return`, `Win Rate`, `Total Trades` und `Avg Trade Return` als Balken-Charts visualisiert.

### Export

**Performance Summary** exportiert alle Kennzahlen und Trading-Parameter als CSV. **Timeseries Data** enthält tägliche Kapitalwerte aller Strategien. **Pairs Analysis** bietet detaillierte Pair-Performance-Daten nach Window-Auswahl. Zusätzlich werden Code-Beispiele für statistische Analysen wie t-Tests, Konsistenz-Analysen und Sharpe Ratio Berechnungen bereitgestellt.

****

## Strategy Creator Tab

Der Strategy Creator ermöglicht die automatisierte Erstellung von Trading-Strategien durch die Ausführung vorkonfigurierter Jupyter Notebooks mit anpassbaren Parametern.

{{< anchor "window" >}}
{{< figure src="/images/gif/fin.gif" 
          >}}

### Workflow 

Der Strategy Creator führt Sie durch einen strukturierten Prozess zur Strategieerstellung. Wählen Sie zunächst den gewünschten Markt und das Strategy Template aus den verfügbaren Jupyter Notebooks. Die Parameter werden automatisch aus dem Notebook extrahiert und als Eingabefelder angezeigt - passen Sie diese nach Ihren Anforderungen an.

Vergeben Sie einen aussagekräftigen Namen für Ihre Strategie über **Strategy Type** und **Strategy Description**. Der **Output Filename** wird automatisch generiert, kann aber manuell angepasst werden. Nach dem Klick auf **"🚀 Run Strategy Creation"** wird ein Background-Job gestartet, der das Notebook mit Ihren Parametern ausführt.

Der Ausführungsprozess läuft vollständig im Hintergrund ab: Zuerst werden die Marktdaten aus dem MinIO Storage heruntergeladen, dann wird das Jupyter Notebook mit Ihren konfigurierten Parametern ausgeführt, und schließlich wird die generierte Strategie-Datei mit entsprechenden Metadaten-Tags zurück in den Storage hochgeladen. Sie können die Seite während der Ausführung verlassen - die Jobs laufen weiter.

### Job Monitoring 

Nach dem Klick auf **"Run Strategy Creation"** wird ein Background-Job gestartet. Die **Active Jobs** Tabelle zeigt alle laufenden und abgeschlossenen Jobs mit farbkodierten Status-Pills: `pending` (gelb), `running` (blau), `completed` (grün) und `failed` (rot). Zusätzlich werden Progress-Informationen und Status-Meldungen angezeigt.

Jobs durchlaufen folgende Phasen: Download der Marktdaten aus MinIO, Notebook-Ausführung mit konfigurierten Parametern, Upload der generierten Strategie-Datei zurück zu MinIO mit entsprechenden Metadaten-Tags. Der **"Refresh Jobs"** Button aktualisiert die Job-Liste manuell, zusätzlich erfolgt eine automatische Aktualisierung alle 10 Requests.

****

## Strategy Templates & Parameter Guide

Übersicht über verfügbare Trading-Strategien und deren konfigurierbare Parameter.

### Cointegration Z-Score Evolution

Diese Strategie identifiziert kointegrierte Aktienpaare und handelt basierend auf Z-Score-Schwellenwerten. Der `p_threshold` (Standard: 0.05) bestimmt das Signifikanzniveau für den Kointegrationstest, wobei niedrigere Werte eine strengere Paarauswahl bedeuten. Die `min_pairs` (20) legt die Mindestanzahl zu handelnder Paare pro Window fest, während `window_shifts` (12) die Anzahl rollierender Analysefenster für das Walk-Forward-Backtesting definiert. Die Handelssignale werden durch `entry_threshold` (2.0) und `exit_threshold` (0.5) als Z-Score-Schwellenwerte gesteuert. Für die Z-Score-Berechnung werden `window1` (5) als kurzes und `window2` (60) als langes gleitendes Mittel verwendet. Der `shift_size` (1) bestimmt die Verschiebung zwischen den Analysefenstern in Monaten.

### Cointegration mit Bollinger Bands
Diese Variante nutzt Bollinger Bänder anstatt fixer Z-Score-Schwellenwerte für dynamischere Handelssignale. Der `std_dev` (2.0) fungiert als Standardabweichungs-Multiplikator für die Bollinger Bänder, während `exit_std_dev` (0.5) die Ausstiegsschwelle definiert. Das `window_size` (20) bestimmt das Berechnungsfenster für die Bollinger Bänder. Zusätzlich werden Hedge Ratios dynamisch angepasst: `hr_window` (25) definiert das Neuberechnungsfenster und `hr_recalc` (3) das Intervall für die Neuberechnung in Tagen. Dies ermöglicht eine bessere Anpassung an sich ändernde Marktbedingungen.

### Affinity Propagation Clustering mit Z-Score

Diese Methode verwendet Clustering für die Paarfindung statt direkter Kointegration. Die Strategie kombiniert die Cluster-Analyse mit klassischen Z-Score-Handelssignalen. Die Parameter `entry_threshold` (2.0) und `exit_threshold` (0.5) funktionieren wie bei der Standard-Z-Score-Strategie, jedoch werden die Paare intelligent über Clustering vorsortiert, was zu stabileren Handelsbeziehungen führen kann.

### Affinity Propagation mit Bollinger Bands
Diese Strategie kombiniert Clustering-basierte Paarfindung mit Bollinger Band-Signalen. Der `std_dev` (2) und `exit_std_dev` (0.5) Parameter steuern die Bollinger Band-Breite für Entry und Exit-Signale. Das `window` (50) definiert das Berechnungsfenster für die Bollinger Bänder. Die dynamische Hedge Ratio-Anpassung erfolgt über `hr_window` (25) und `hr_recalc` (3), was besonders bei cluster-basierten Paaren wichtig ist, da diese möglicherweise verschiedene Beta-Verhältnisse aufweisen.

### Gradient Boosting Z-Score Evolution
Diese Machine Learning-basierte Strategie nutzt Gradient Boosting für intelligente Paarpriorisierung. Die ML-Parameter umfassen `learning_rate` (0.2) für die Lerngeschwindigkeit, `max_depth` (2) für die maximale Baumtiefe zur Overfitting-Vermeidung, sowie `min_samples_leaf` (2) und `min_samples_split` (2) zur Kontrolle der Baumkomplexität. Der `n_estimators` (300) Parameter bestimmt die Anzahl der Bäume im Ensemble. Das Modell lernt aus historischen Daten, welche Paare die besten Handelsergebnisse liefern, und priorisiert diese entsprechend.

### Gradient Boosting mit Bollinger Bands
Diese Strategie kombiniert ML-basierte Paarauswahl mit Bollinger Band-Trading. Der `bb_window` (50) definiert das Bollinger Band-Fenster, während `std_dev` (1.5) einen konservativeren Multiplikator verwendet als andere Strategien. Die Gradient Boosting-Parameter sind identisch zur Z-Score-Variante, jedoch wird das Modell auf Bollinger Band-spezifische Features trainiert, was zu präziseren Entry- und Exit-Zeitpunkten führen kann.