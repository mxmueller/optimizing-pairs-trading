---
title: "Ausarbeitung"
math: true  # Das aktiviert KaTeX (ist schon im Theme)
---

Pairstrading ist eine nichtdirektionale Handelsstrategie, die unabhängig von der Marktrichtung funktioniert {{< cite ref="Vidyamurthy 2004" page="p. 8" >}}. Sie basiert auf historischen Zusammenhängen zwischen zwei Wertpapieren (Zeitreihen) $X_i(t)$ und $X_j(t)$ und nutzt temporäre Abweichungen in deren Preisbeziehung zur Gewinnerzielung aus. Im verbreiteten, statistischen Pairstrading werden zwei Hauptansätze unterschieden: kointegrationsbasierte und korrelationsbasierte Verfahren. {{< cite ref="Engle 1987" etal="true" noparen="true">}} legten die theoretischen Grundlagen der Kointegration, {{< cite ref="Vidyamurthy 2004" etal="true" noparen="true">}} entwickelten deren Anwendung im Pairstrading, und {{< cite ref="Gatev 2006" etal="true" noparen="true">}} etablierten den korrelationsbasierten Ansatz. Pairstrading umfasst zwei fundamentale Schritte: das Identifizieren geeigneter Paare und deren Handel.


### Der Kointegrationsansatz
Die Cointegration hat nichts mit der "Integration" zu tun wie der Name vermuten lässt. Nach {{< cite ref="Engle 1987" etal="true" noparen="true">}} werden Paare auf eine langfristige Gleichgewichtsbeziehung getestet. Die Zeitreihen können kurzfristig voneinander abweichen, werden jedoch in der thorie durch ökonomische Kräfte langfristig zusammengehalten.

{{< anchor "cointpair" >}}
**Cointegrierte Paare finden:** Um solche Beziehungen zu identifizieren, wird zunächst eine Regressionsgleichung geschätzt: 
<a id="f1"></a>
$$X_i(t) = \alpha_{i,j} + \beta_{i,j} X_j(t) + \varepsilon_{i,j}(t)$$

Die Residuen $\varepsilon_{i,j}(t)$ dieser Regression müssen stationär sein, auch wenn die ursprünglichen Zeitreihen $X_i(t)$ und $X_j(t)$ selbst nichtstationär sind. Ein stationärer Prozess kehrt zu seinem Mittelwert zurück und weist konstante Varianz auf. Mit dem Engle-Granger-Verfahren {{< cite ref="Engle Granger 1987" cf="true" >}} wird diese Stationarität der Residuen mittels Augmented Dickey-Fuller-Test {{< cite ref="Dickey 1979" cf="true" >}} geprüft. Die Nullhypothese lautet, dass die Residuen eine Einheitswurzel besitzen (nichtstationär sind). Wird diese Nullhypothese bei einem Signifikanzniveau $\alpha_{\text{sig}}$ verworfen ($p$-Wert $< \alpha_{\text{sig}}$), liegt Kointegration vor. 

**Cointegrierte Paare handeln:** Aufgrund ihrer statistischen Eigenschaften (stabilisieren die Varianz) werden die Preise logarithmisch mit $\log X_i(t)$ und $\log X_j(t)$ angewandt. Um das optimale Verhältnis für einen Trade zu finden, wird die Hedge Ratio durch lineare Regression bestimmt:
<a id="f2"></a>
$$\log X_i(t) = \alpha_{i,j} + \beta_{i,j} \log X_j(t) + \varepsilon_{i,j}(t)$$

Wobei $\alpha_{i,j}$ die Konstante (Intercept der Regression), $\beta_{i,j}$ das Hedge Ratio (gibt an, wie viele Einheiten von $X_j$ pro Einheit $X_i$ gehandelt werden) und $\varepsilon_{i,j}(t)$ der Fehlerterm (Residuen) ist. Das Hedge Ratio $\beta_{i,j}$ hat den Zweck, dass Long- und Short-Positionen marktneutral sind. Mit dem Hedge Ratio kann nun ein marktneutraler Spread konstruiert werden:
<a id="f3"></a>
$$Spread_{i,j}(t) = \log X_i(t) - \beta_{i,j} \log X_j(t)$$

Dieser Spread eliminiert die gemeinsame Marktbewegung. Damit Trading damit aber profitabel ist, muss der Spread mean-reverting (mittelwertrückkehrend) sein:
<a id="f4"></a>
$$Spread_{i,j}(t) = \mu_{i,j} + u_{i,j}(t)$$

wobei $u_{i,j}(t)$ ein stationärer Prozess mit $E[u_{i,j}(t)] = 0$ ist. Im Handel können profitable Abweichungen nur realisiert werden, wenn der Spread zum Mittelwert zurückkehrt. Um feststellen zu können, wann der Spread zu weit von seinem Mittelwert entfernt ist, wird er normalisiert:
<a id="f5"></a>
$$Z_{i,j}(t) = \frac{Spread_{i,j}(t) - \mu_{i,j}}{\sigma_{i,j}}$$
Der Z-Score macht Abweichungen vergleichbar und definiert klare Ein- und Ausstiegssignale. Als Beispiel bei $\theta = 2$: Long bei $Z_{i,j}(t) < -\theta$ mit Long $X_i$, Short $\beta_{i,j} \cdot X_j$ oder Short bei $Z_{i,j}(t) > +\theta$ dann vice versa Short $X_i$, Long $\beta_{i,j} \cdot X_j$. Der Exit solcher Trades erfolgt bei $Z_{i,j}(t) \rightarrow 0$, da der Spread zur historischen Mitte zurückkehrt.

### Der Korrelationsansatz
Nach {{< cite ref="Gatev 2006" etal="true" noparen="true">}} basiert der korreltaionsansatz auf der Annahme, dass $X_i(t)$ und $X_j(t)$ mit historisch hoher Korrelation auch in Zukunft eine ähnliche Preisbewegung aufweisen werden. Im Gegensatz zu kointegrationsbasierten Ansätzen wird hier keine langfristige Gleichgewichtsbeziehung vorausgesetzt sondern kurzfristige Korrelationsbezeihungen angenommen. 

**Korrealierende Paare finden:** Bei korrelationsbasierten Verfahren erfolgt die Paarauswahl nach {{< cite ref="Sharpe 1964" noparen="true">}} mittels der Pearson-Korrelation in einer Formationsperiode der Länge $t_f$:
{{< anchor "f6" >}}
$$\rho_{i,j} = \frac{Cov(X_i, X_j)}{\sigma_{X_i} \sigma_{X_j}} = \frac{\sum_{t=1}^{t_f}(X_i(t) - \bar{X_i})(X_j(t) - \bar{X_j})}{\sqrt{\sum_{t=1}^{t_f}(X_i(t) - \bar{X_i})^2}\sqrt{\sum_{t=1}^{t_f}(X_j(t) - \bar{X_j})^2}}$$

wobei $\bar{X_i}$ und $\bar{X_j}$ die Mittelwerte der jeweiligen Zeitreihen in der Formationsperiode darstellen. Paare mit $\rho_{i,j} > \rho_{\min}$ oberhalb eines definierten Schwellenwerts werden für das Trading ausgewählt.

**Korrelierte Paare handeln:**
Für das Handeln der Paare nach {{< cite ref="Gatev 2006" etal="true" noparen="true">}} werden die Zeitreihen zunächst normalisiert. Die kumulative Summe[^1] der logarithmierten Renditen wird durch ihre historische Standardabweichung geteilt:
 
$$Z_k(t) = \frac{\sum_{s=1}^{t} \log\frac{X_k(s)}{X_k(s-1)}}{\sigma_k} \quad \text{für } k \in \{i,j\}$$

wobei $\sigma_i$ und $\sigma_j$ die Standardabweichungen der logarithmierten Renditen in der Formationsperiode sind. Der Spread zwischen den normalisierten Zeitreihen wird als Divergenz definiert: $D_{i,j}(t) = Z_i(t) - Z_j(t)$. Wenn die Divergenz einen Schwellenwert $\delta$ überschreitet werden entsprechende Handelssignale erzeugt. Long von $X_i$ und Short $X_j$ bei $D_{i,j}(t) < -\delta$ und Long von $X_j$ und Short $X_i$ bei $D_{i,j}(t) < +\delta$. Die Positionen werden geschlossen, wenn die Divergenz gegen null konvergiert ($D_{i,j}(t) \rightarrow 0$).

****

# Ziel oder Motivation
**Drei zentrale Faktoren** reduzieren die Profitabilität statischer Pairstrading-Anwendungen im modernen Marktumfeld: 

1. **Popularität:** Je mehr Marktteilnehmer dieselbe Strategie nutzen, desto schneller verschwinden die Arbitragemöglichkeiten {{< cite ref="Jacobs 2015" cf="true" >}}. Die Anwendung von Pairs trading steigt seit Anfang der 2000er Jahre nachweisbar bei professional traders, institutional investors, and hedge fund managers {{< cite ref="Miao 2014" page="p. 96" >}}.

2. **Eliminierung von Ineffizienzen:** {{< cite ref="Miao 2014" etal="true" noparen="true" >}} verdeutlicht, wie High Frequency Handel (*HFT*) durch technologischen Fortschritt Markteffizienzen eliminiert. Während bei der Entwicklung der kointegrationsbasierten und korrelationsbasierten Ansätze Positionen über Wochen oder Tage gehalten wurden, werden heute Arbitragemöglichkeiten binnen Stunden, Minuten oder sogar Sekunden ausgenutzt. Die Ineffizienzen, auf denen klassisches Pairs Trading basiert, werden schneller erkannt und eliminiert, bevor traditionelle Ansätze reagieren können.

3. **Instabilität:** {{< cite ref="Chen 2019" etal="true" noparen="true" >}} zeigen, dass Kointegrationsbeziehungen zwischen Aktienpaaren nicht stabil sind, sondern sich durch Regime-Wechsel grundlegend verändern oder vollständig verschwinden können. Marktbedingungen wechseln zwischen verschiedenen Zuständen - von kointegrierenden Beziehungen hin zu Black-Scholes-ähnlichen Märkten ohne statistische Arbitragemöglichkeiten.

Diese Herausforderungen eröffnen spezifische Ansatzpunkte zur Weiterentwicklung. Aufgrund der Ressourcen institutioneller High Frequency Handelsysteme macht es im Kontext der Markteffizienzen keinen Sinn, an den Handelsstrategien für vorhandene Paarfindungsstrategien direkt anzusetzen. Die Annahme ist, dass sobald eine Ineffizienz besteht, verschiedene Handelsstrategien zu ihr führen können, diese aber immer von Ressourcen (Rechen- und Übertragungsgeschwindigkeit) geschlagen werden können. Kommulieren eine großer Anteil der Marktteilnehmer durch die verwendung Dokumentierter und in der Vergangenheit erfolgreicher Verfahren wie der Cointegration, Korrelationen oder ihren Weiterentwicklungen, entstehen "crowded trades", die bei ersten Verlusten zu gleichzeitigen Liquidationen und Verlustververstärkungen führen. Daher lautet die Hypthese dieser Arbeit die Profitabilitat und Optimizierung des Pairs Trading darin liegen kann, Paare finden zu können die durch diese traditionell statistischen Ansätze sonst verborgen bleiben. Zur Bewältigung der Instabilitätsproblematik werden adaptive Ansätze mit rollenden Fenstern und dynamischen Parametern eingesetzt, die sich kontinuierlich an veränderte Marktregime anpassen können. Das führt zur folgenden Forschungsfrage: 
> Inwieweit verbessert ein maschineller Lernansatz zur Paaridentifikation die Performance von Pairs Trading Strategien im Vergleich zu traditionellen kointegrationsbasierten Verfahren? 

Als explorative Arbeit ist die Vorgabe der maschinellen Lernansätze bewusst offen gehalten. Am Ende konnten zwei Ansätze erarbeitet werden: ein [Affinity propagation Clustering](#ML1) und [Gradient Boost Regressor](#ML2) Verfahren. Diese werden mit einem kointegrationsbasierten, nach {{< cite ref="Engle 1987" etal="true" noparen="true">}} implementierten Ansatz verglichen. Dieser erhält jedoch zur Vergleichbarkeit ebenfalls die Anwendung des [Sliding Window Ansatzes](#Window). Vergleichsstudien begründen die Auswahl durch validierte Überlegenheit der Kointegrationsverfahren gegenüber der Korrelation {{< cite ref="Rad 2016">}}; {{< cite ref="Carrasco Blázquez 2018">}}; {{< cite ref="Ma 2022">}}.

****

# Data
Um eine Teilmenge an Zeitreihen (Wertpapieren, Aktien oder sonstigem) zu erhalten auf die dann Verfahren zur Paarbildung angewendet werden können verwenden vergleichbare Arbeiten Vorauswahlen wie den Global Industry Classification Standard (GICS) {{< cite ref="Do 2010" page="p. 8" >}}.

{{< anchor "economy-chart" >}}
![Alt-Text](/images/economy.drawio.png "Abbildung 1: Systematische Darstellung der Wirtschaftsstruktur mit den Klassifikationsebenen: 1. Global Industry Classification Standard (*GICS*); 2. Nationale Sektoren (Primär-, Sekundär, Tertiärer-sektor); 3. Hierarchische Industriestruktur (Industriezweig; Industrie, Subindustrie); 4. Inländische Aktienindizes im Kontext der globalen und nationalen Wirtschaft.")

*GICS* bildet die Basis für S&P und MSCI Finanzmarkt-Indizes, in denen jede Firma gemäß ihrer Hauptgeschäftstätigkeit genau einer Subindustrie und damit einer Industrie, einem Industrie-Zweig und einem Sektor zugewiesen ist. Die Eingrenzung an potenziellen Paaren bildet sich dann in den jeweils durch die Klassifizierung festgelegten Sektoren bzw. Subsektoren (siehe [Abbildung 1, siehe 3](#economy-chart)). So können zwar wirtschaftliche Synergien in den Paaren vorliegen, jedoch können potenzielle Verbindungen von vornherein fälschlicherweise ausgeschlossen werden. Um diese Ausgrenzung größtmöglich zu abstrahieren, geschieht die Vorauswahl auf nationaler volkswirtschaftlicher Ebene (siehe [Abbildung 1, siehe 2](#economy-chart)). Diese bewusste Entscheidung gegen sektorspezifische Vorfilterung folgt der Hypothese, dass maschinelle Lernverfahren auch branchenübergreifende Zusammenhänge identifizieren können, die durch traditionelle GICS-basierte Einschränkungen ausgeschlossen würden. Im Rahmen dieser Arbeit geschieht dies im Rahmen des amerikanischen und britischen Marktes in Form des *NASDAQ-100* und *FTSE-100* (im Nachfolgenden abgekürzt als $N_{100}$
​ und $F_{100}$) (siehe [Abbildung 1, siehe 4](#economy-chart)).

**Indizes:** Die Aktiendaten beider Indizes erstrecken sich über den Zeitraum $T = [t_{\text{start}}, t_{\text{end}}]$, wobei $t_{\text{start}}$ dem 01.01.2020 und $t_{\text{end}}$ dem 01.01.2025 entspricht. Für jede Aktie wird an jedem Handelstag ein vollständiger Datensatz erfasst, der das Handelssymbol, das Datum sowie die wesentlichen Kursinformationen umfasst: Eröffnungskurs, Tageshöchstkurs, Tagestiefstkurs, Schlusskurs und Handelsvolumen. Da keine weiteren Einschränkungen bezüglich Marktkapitalisierung, Liquidität oder Branchenzugehörigkeit vorliegen, ergibt sich aus dem Pool aller 100 Aktien eines Index $A = \{a_1, a_2, ..., a_{100}\}$ die Menge aller zulässigen Paare durch $P = \{(a_i, a_j) \mid a_i, a_j \in A \land i < j\}$. Dies entspricht $\binom{100}{2} = 4950$ möglichen Paarkandidaten pro Index.

{{< anchor "indices" >}}
![Alt-Text](https://placehold.co/200 "Abbildung 2: Die Abbildung zeigt die normalisierten Marktindizes $F_{100}$ und $N_{100}$ (2020-2025, Basis=100) mit Gesamtwachstum ($F_{100}$: +30,1%, $N_{100}$: +107,1%) und hervorgehobenem Wachstum im Jahr 2024 von $F_{100}$: +7,9%, $N_{100}$: +15,8%.")

**Datenbereinigung:** Zeitreihen, die nicht die vollständige Anzahl an Datenpunkten für den Zeitraum $T = [t_{\text{start}}, t_{\text{end}}]$ vorweisen können, wurden ausgelassen. Das resultierte für $N_{100}$ in 94 und $F_{100}$ in 98 Aktien pro Index. Der Umgang mit vereinzelt fehlenden Werten erfolgt anhand der Kurszeitreihen $X_i(t)$ für jede Aktie $i$. Eine Vorwärtsinterpolation ersetzt fehlende Werte durch den letzten verfügbaren Wert derselben Zeitreihe: $X_i(t) = X_i(t-k)$, wobei $k$ die kleinste positive Zahl ist, für die $X_i(t-k)$ beobachtet wurde. Anschließend werden bestehende Lücken durch nachfolgende Werte aufgefüllt: $X_i(t) = X_i(t+m)$, wobei $m$ die kleinste positive Zahl ist, für die $X_i(t+m)$ beobachtet wurde. Im Vergleich zu anderen Methoden wie der linearen oder polynomialen Interpolation bietet die Vorwärts- und Rückwärtsinterpolation eine robuste Lösung für Finanzzeitreihen, da sie ausschließlich beobachtete Werte verwendet und so die Kontinuität der Daten bewahrt {{< cite ref="Moritz 2017" >}}. Der bereinigte, normalisierter Kursverlauf aller vorhanden Werte pro Indices kann [Abbildung 2](#indices) entnommen werden.

****

# Affinity Propagation Clustering Approach 
Affinity Propagation ist ein exemplarbasiertes Clustering-Verfahren, das durch iterative Nachrichtenübertragung zwischen Datenpunkten automatisch die optimale Clusteranzahl bestimmt und repräsentative Exemplare aus den Daten selbst auswählt. Der Algorithmus maximiert Ähnlichkeitssummen durch Nachrichtenaustausch, der bewertet wie gut Datenpunkte als Cluster-Zentren geeignet sind und wie bereit andere sind, diese zu akzeptieren {{< cite ref="Dueck 2009" >}}.

Die Auswahl erfolgte aus zwei Gründen: Erstens ermöglicht die automatische Clusterbestimmung beim Sliding Window Verfahren eine flexible Anpassung der Clusteranzahl zwischen Zeitfenstern. Zweitens existiert bisher nur eine dokumentierte Anwendung zur Paarfindung im Pairs Trading, aber in abgewandelter Form und im Cryptocurrency-Markt {{< cite ref="Othman 2025" >}}. Mithilfe des Silhouette Score wurde auf Basis der Hauptmerkmale Rendite und Volatilität ausgewählt. Diese werden nach Ihrer gänigen Form angewandt:

$$\text{Rendite} = R_i = \frac{1}{T} \sum_{t=1}^{T} \frac{P_t - P_{t-1}}{P_{t-1}} \times \text{Handelstage pro Jahr}$$
$$\text{Volatilität} = V_i = \sqrt{\frac{1}{T-1} \sum_{t=1}^{T} \left( \frac{P_t - P_{t-1}}{P_{t-1}} - \mu \right)^2} \times \sqrt{\text{Handelstage pro Jahr}}$$

Die wirtschaftliche Annahme ist, dass Aktien mit ähnlichen Risiko-Rendite-Profilen vergleichbar auf Marktbedingungen reagieren und daher stabilere statistische Beziehungen aufweisen als willkürlich gewählte Paare. Das Clustering reduziert den Suchraum wenige hundert Paarkombinationen innerhalb der Cluster, wodurch das Multiple-Testing-Problem minimiert wird. 

{{< anchor "cluster2" >}}
{{< figure src="/images/oo2.drawio.png" 
           caption="Abbildung 3: Affinity Propagation Clustering für $F_{100}$ Aktien im Rendite-Volatilität-Raum mit exemplar-basierten Cluster-Zentren."
          >}}

[Abbildung 3](#cluster2)) zeigt das Affinity Propagation Clustering im originalen Rendite-Volatilität-Raum für den $F_{100}$. Die Verbindungslinien verdeutlichen die exemplar-basierte Struktur: jede Aktie ist mit ihrem Cluster-Zentrum verbunden, wobei die Zentren selbst Aktien aus dem Datensatz sind (nicht berechnete Mittelwerte). Eine mögliche ökonimische interpretierbarkeit dieser Cluster ist mithilfe der Rendite-Volatilität-Quadranten auf der rechten Seite der grafik zu sehen. 

Kointegrationstests bleiben notwendig, da ähnliche Rendite-Volatilität-Profile nicht automatisch langfristige Gleichgewichtsbeziehungen garantieren - das Clustering dient als ökonomisch motivierte Vorauswahl für statistisch robuste Paare mit lokaler aussagekraft(siehe [Abbildung 3](#cluster1)).
Die Auswahl eines Paares erfolgt nach erfolgt durch einen gewichteten Score aus Cluster-Zentrumsabstand und Profil-Ähnlichkeit: 

{{< anchor "score" >}}
$$S_{i,j} = 0.6 \cdot D_{center,norm} + 0.4 \cdot D_{profile,norm}$$


wobei $D_{center}$ den durchschnittlichen euklidischen Abstand beider Aktien zum Cluster-Zentrum $C$ und $D_{profile}$ die direkte euklidische Distanz zwischen den Aktien im standardisierten Rendite-Volatilität-Raum misst. Beide Komponenten werden min-max-normalisiert und nur Paare mit [Kointegrations](#cointpair)-$p$-Wert $< 0.05$ werden für das Trading ausgewählt.

{{< anchor "cluster3" >}}
{{< figure src="/images/output4.png" 
           caption="Abbildung 4: Selektierte Trading-Paare nach Kointegrationstest und Score-Bewertung im t-SNE Ähnlichkeitsraum."
           width="650" 
           style="text-align: center; margin: 0 auto;" >}}

[Abbildung 4](#cluster3) reduziert in ihrer Darstellung nach der [Score Bewertung](#score) und [Kointegrationstest](#cointpair) selektierten Akien. Die t-SNE Transformation projiziert diese in einen Ähnlichkeitsraum, der lokale Nachbarschaften besser sichtbar macht und die entgültigen Paare eines Fensters beispielhaft zeigt.

HIER NOCH KONFIGURATION??

# Gradient Boost Regressor Verfahren
Der Gradient Boost Regressor versucht schrittweise viele schwache Entscheidungsbäume zu einem starken Vorhersagemodell zu kombinieren, wobei jeder neue Baum die Residuen (Differenz zwischen tatsächlichen und vorhergesagten Werten) der vorherigen Bäume als Zielvariable verwendet. Das Verfahren analysiert in jeder Iteration systematisch, in welche Richtung die Vorhersagen korrigiert werden müssen, um die Fehler zu minimieren, und trainiert einen neuen Entscheidungsbaum, der genau diese Korrekturen lernt und zur Gesamtvorhersage hinzuaddiert wird {{< cite ref="He 2019" >}}.


Zum Zeitpunkt der Erstellung dieser Arbeit gibt es keinen vergleichbaren Einsatz zur Parrfindung in der Literatur. Arbeiten wie die von {{< cite ref="Krauss 2017" etal="true" cf="true" noparen="true" >}} mit dem Titel *"Deep neural networks, gradient-boosted trees, random forests: Statistical arbitrage on the S&P 500"* zeigen dass Gradient-Boosted Trees mit 0.37% täglichen Renditen vor Transaktionskosten sowohl Deep Neural Networks (0.33%) als auch Random Forests (0.43%) in Statistical Arbitrage Strategien übertreffen. Daher zeigt das Verfahren Potential auch im Pairs Trading erfolgreich angewendet werden zu können. 

Der Regressor nutzt ein mehrdimensionalen Feature Vektor zur Vorhersage der durchschnittlichen Spread-Abweichung zwischen Aktienpaaren. Die Auswahl dieser Zielvariablen folgt nach der validierung als Targetvariable in verwandten Arbeiten des Maschine Learning in Verbinduzng mit statistical abitrage {{< cite ref="Sarmento 2020" >}}; {{< cite ref="Lin 2021" >}}. Die empirischen Befunde zeigen, dass Preisdifferenzen zwischen kointegrierteren Aktien beim klassischen Pairs Trading nicht konvergieren, sondern persistieren und damit Verluste verursachen. Herkömmliche Verfahren messen Spreads, definieren Schwellenwerte und reagieren reaktiv darauf. Machine Learning-Ansätze prognostizieren hingegen Aktienpaare mit künftig minimaler Spread-Volatilität. Anstatt sämtliche kointegrierten Paare zu handeln und deren Konvergenz abzuwarten, selektiert das Modell ausschließlich Paare mit prognostizierter Spread-Stabilität.

Die finale Feature-Matrix umfasst 32 Dimensionen. 3 statistische Basis-Features, 20 technische Zeitreihen-Indikatoren, 6 Volume-Eigenschaften und 3 erweiterte MACD-Komponenten. Fehlende Werte werden durch SimpleImputer mit Mittelwert-Strategie behandelt:

| Feature | Beschreibung |
|:------------------|:-------------|
| **`Korrelation`** | Nutzt die bereits eingeführte [Pearson-Korrelation](#f6) aus dem Korrelationsansatz, jedoch nicht als Selektionskriterium mit festem Schwellenwert $ρ_{min}$, sondern als kontinuierliches Feature. |
| **`Beta`** | Sensitivitätsverhältnis: $R_{i,t} = α + β_{i,j} · R_{j,t} + ε_t$ aus der Regression. |
| **`Residual-Standardabweichung`** | Die Präzision dieser linearen Beziehung. |
| **`Rate of Change`** | Prozentuale Preisänderungen über 5, 20 und 50 Tage für beide Aktien sowie deren Differenzen. |
| **`Williams Oszillatoren`** | Relative Position aktueller Preise über 10, 14, 28 und 40 Tage für beide Aktien sowie deren Differenzen. |
| **`Bollinger Bands`** | Spread-Volatilität relativ zum gleitenden Durchschnitt für 5, 10, 20, 25 und 50 Tage. |
| **`Moving Average Convergence/Divergence`** | Trend-Momentum mit Parametersätzen (12,26,9) und (5,13,5). Erfasst werden Liniendifferenzen, Signalliniendifferenzen und binäre Crossover-Signale für beide Aktien. |
| **`Volumen Rate of Change`** | Momentum-Indikatoren über 5, 20 und 50 Tage für beide Aktien sowie deren Differenzen. |
| **`Volumen-Durchschnitte und Standardabweichungen`** | Gleitende Mittelwerte und Streuungsmaße für 50 und 100 Tage. |
| **`Volumen-Änderungen`** | Prozentuale Veränderungen für 50 und 100 Tage. |

Die auswahl dieser Features und ihrer Zeitfenster ergab sich aus einem zweistufigem Optimierungsprozess. Ein Feature-Set von 80 technischen Indikatoren mit unterschiedlichen Zeitfenster wurde mithilfe der `Gradient Boosting Feature Importance Analyse` evaluiert. Aus der initialen Feature Importance Rangfolge wurden die 32 leistungsstärksten Merkmale selektiert, wobei redundante Features mit hoher Korrelation eliminiert wurden.

##### Implementierung
Die Hyperparameter des finalen Models umfassen `learning_rat` von `0.2`, `max_depth` von `2` und `n_estimators` von `300` Bäumen, sowie `n_estimators` und `min_samples_leaf` von jeweil `2`. Die Parameterauswahl erfolgte durch eine Grid Search `learning_rate` $∈ {0.01, 0.1, 0.2}$, `max_depth` $∈ {2, 3, 4}$, `n_estimators` $∈ {100, 200, 300}$ und Regularisierungsparameter `min_samples_split` $∈ {2, 4}$ sowie `min_samples_leaf` $∈ {1, 2}$. Eine 5 Fache Kreuzvalidierung mit $R²$-Score als Optimierungsmetrik ergab die finale Konfiguration. Das Training erfolgt auf 80% der verfügbaren Daten  20% Test-Set-Evaluation.

{{< anchor "regressor" >}}
{{< figure src="/images/regressorv1.drawio.png" 
           caption="Abbildung 5: Predicted vs Actual Darstellung der Gradient Boosting Modelle für $N_{100}$ (links) und $F_{100}$ (rechts). Die lineare Beziehung zwischen vorhergesagten und tatsächlichen Spread-Abweichungen bestätigt die Vorhersagequalität beider Modelle."
           style="text-align: center; margin: 0 auto;" >}}

 Die Predicted vs Actual Darstellungen in [Abbildung 5](#regressor) bestätigen die solide Vorhersageleistung beider Modelle. Das $N_{100}$ Modell erreicht ein `R²` von `0.707` mit einem `MSE` von `0.068` und `MAE` von `0.201`, während das $F_{100}$ Modell ein `R²` von `0.652` bei einem `MSE` von `0.084` und `MAE` von `0.227` erzielt.



# Window

# Data

















## Cite Example

bla [Zur Kostenfunktion](#cost-function)
Machine Learning {{< cite "Smith 2023" >}} ist wichtig.

<!-- Verlinkt zu "Engle Granger 1987" aber zeigt "et al." -->
{{< cite ref="Engle Granger 1987" cf="true" >}}

<!-- Mit Seite -->
{{< cite ref="Engle Granger 1987" etal="true" page="S. 255" >}}

<!-- Ohne Klammern -->
Laut {{< cite ref="Jacobs 2015" etal="true" cf="true" noparen="true" page="S. 255">}} ist...

<!-- FUßNOTEN -->
[^1]: Die kumulative Summe der Log-Renditen ist die laufende Aufsummierung aller bisherigen Renditen und zeigt, wie sich der Preis insgesamt vom Startpunkt verändert hat.


## Literatur
{{< reference "Sharpe 1964" >}}Sharpe, W. F. (1964). Capital Asset Prices: A Theory of Market Equilibrium Under Conditions of Risk. The Journal of Finance, 19(3), 425-442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x{{< /reference >}}

{{< reference "Dickey 1979" >}}Dickey, D. A., & Fuller, W. A. (1979). Distribution of the Estimators for Autoregressive Time Series with a Unit Root. Journal of the American Statistical Association, 74, 427-431. https://api.semanticscholar.org/CorpusID:56458593{{< /reference >}}

{{< reference "Engle 1987" >}}Engle, R. F., & Granger, C. W. J. (1987). Co-integration and Error Correction: Representation, Estimation, and Testing. Econometrica, 55(2), 251-276. https://ideas.repec.org/a/ecm/emetrp/v55y1987i2p251-76.html{{< /reference >}}

{{< reference "Vidyamurthy 2004" >}}Vidyamurthy, G. (2004). Pairs Trading: Quantitative Methods and Analysis. John Wiley & Sons, Hoboken, New Jersey.{{< /reference >}}

{{< reference "Gatev 2006" >}}Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). Pairs Trading: Performance of a Relative Value Arbitrage Rule. Yale ICF Working Paper No. 08-03. https://doi.org/10.2139/ssrn.141615{{< /reference >}}

{{< reference "Dueck 2009" >}}Dueck, D. (2009). Affinity propagation: Clustering data by passing messages. PhD thesis.{{< /reference >}}

{{< reference "Do 2010" >}}Do, B., & Faff, R. (2010). Does simple pairs trading still work? Financial Analysts Journal, 66(4), 83-95. https://doi.org/10.2469/faj.v66.n4.1{{< /reference >}}

{{< reference "Miao 2014" >}}Miao, G. J. (2014). High frequency and dynamic pairs trading based on statistical arbitrage using a two-stage correlation and cointegration approach. International Journal of Economics and Finance, 6, 96. https://api.semanticscholar.org/CorpusID:54175142{{< /reference >}}

{{< reference "Jacobs 2015" >}}Jacobs, H., & Weber, M. (2015). On the determinants of pairs trading profitability. Journal of Financial Markets, 23, 75-97. https://doi.org/10.1016/j.finmar.2014.12.001{{< /reference >}}

{{< reference "Rad 2016" >}}Rad, H., Low, R. K. Y., & Faff, R. (2016). The profitability of pairs trading strategies: distance, cointegration and copula methods. Quantitative Finance, 16(10), 1541-1558. https://doi.org/10.1080/14697688.2016.1164337{{< /reference >}}

{{< reference "Moritz 2017" >}}Moritz, S., & Bartz-Beielstein, T. (2017). imputeTS: Time series missing value imputation in R. The R Journal, 9(1), 207-218. https://doi.org/10.32614/RJ-2017-009{{< /reference >}}

{{< reference "Krauss 2017" >}}Krauss, C., Do, X. A., & Huck, N. (2017). Deep neural networks, gradient-boosted trees, random forests: Statistical arbitrage on the S&P 500. European Journal of Operational Research, 259(2), 689-702. https://doi.org/10.1016/j.ejor.2016.10.031{{< /reference >}}

{{< reference "Carrasco Blázquez 2018" >}}Carrasco Blázquez, M., De la Orden De la Cruz, C., & Prado Román, C. (2018). Pairs trading techniques: An empirical contrast. European Research on Management and Business Economics, 24(3), 160-167. https://doi.org/10.1016/j.iedeen.2018.05.002{{< /reference >}}

{{< reference "He 2019" >}}He, Z., Lin, D., Lau, T., & Wu, M. (2019). Gradient boosting machine: A survey. arXiv preprint arXiv:1908.06951. https://arxiv.org/abs/1908.06951{{< /reference >}}

{{< reference "Chen 2019" >}}Chen, K., Chiu, M. C., & Wong, H. Y. (2019). Time-consistent mean-variance pairs-trading under regime-switching cointegration. SIAM Journal on Financial Mathematics, 10(2), 632-665. https://doi.org/10.1137/18M1209611{{< /reference >}}

{{< reference "Sarmento 2020" >}}Sarmento, S. M., & Horta, N. (2020). Enhancing a pairs trading strategy with the application of machine learning. Expert Systems with Applications, 158, 113490. https://doi.org/10.1016/j.eswa.2020.113490{{< /reference >}}

{{< reference "Lin 2021" >}}Lin, T.-Y., Chen, C. W. S., & Syu, F.-Y. (2021). Multi-asset pair-trading strategy: A statistical learning approach. The North American Journal of Economics and Finance, 55, 101295. https://doi.org/10.1016/j.najef.2020.101295{{< /reference >}}

{{< reference "Ma 2022" >}}Ma, B., & Ślepaczuk, R. (2022). The profitability of pairs trading strategies on Hong-Kong stock market: distance, cointegration, and correlation methods. Working Papers 2022-02, Faculty of Economic Sciences, University of Warsaw. https://ideas.repec.org/p/war/wpaper/2022-02.html{{< /reference >}}

{{< reference "Othman 2025" >}}Othman, A. H. A. (2025). Enhancing pairs trading strategies in the cryptocurrency industry using machine learning clustering algorithms. London Journal of Research In Management & Business, 25(1), 33-52. https://journalspress.uk/index.php/LJRMB/article/view/1179{{< /reference >}}
