# Latency Lab: Zeiten und Wiederholungen

Erkennen Sie langsame Aufgaben und messen Sie zusätzliche Versuche anhand derselben Aufzeichnungen.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/latency.md) · [English](../en/latency.md) · [Deutsch](../de/latency.md)

## Das erhalten Sie

Prüfen Sie je Version die erfassten Aufgabendauern, P50, P95, den Höchstwert und Wiederholungen. Vergleichen Sie dieselben Aufgaben nach Modell- oder Workflowänderungen.

Geben Sie für jeden Versuch die Dauer in Millisekunden unter latency_ms an. duration_coverage ist der Anteil der Aufgaben, für deren sämtliche Versuche eine Dauer vorliegt.

## P50 und P95 verstehen

Die Berechnung addiert die erfassten Versuchsdauern pro Aufgabe, sortiert die Summen und verwendet den aufgerundeten Rang: ceil(0,50 × n) für P50 und ceil(0,95 × n) für P95.

Bei 20 Aufgaben ist P95 beispielsweise der 19. sortierte Wert. Er beschreibt diese Stichprobe und garantiert keine Dauer zukünftiger Anfragen.

## Wiederholungen messen

Erfasste Wiederholungen = Versuche − unterschiedliche Aufgaben, je Variante getrennt berechnet. 40 Aufgaben und 48 Versuche ergeben 8 erfasste Wiederholungen.

Vergleichen Sie retry_attempts mit Ihrem eigenen Wiederholungsbudget. Diese Version misst zusätzliche Versuche; sie konfiguriert keine Wiederholungsgrenze im Agenten und liefert keinen gesonderten Zähler fehlgeschlagener Wiederholungen.

## Eine Zeitgrenze setzen

maxP95LatencyMs in config setzt die Grenze für das erfasste P95. Latency Lab prüft sie je Gruppe; Quality Gate nutzt die Prüfung der Variante candidate für seine Entscheidung.

Fehlt bei einem Versuch die Dauer, werden P50, P95 und Höchstwert der Gruppe null. within_p95_threshold ist null bei unvollständigen Zeiten oder ohne angeforderte Grenze. Ersetzen Sie fehlende Dauern nicht durch null Millisekunden.

## Die Zeitmessung einordnen

Die Summe der Dauern entspricht bei parallelen Versuchen nicht der gesamten Wartezeit eines Nutzers. Nicht erfasste Wartezeiten fehlen ebenfalls.

Das Format verlangt weder Zeitstempel noch eine Reihenfolge. Es kann den ersten Versuch nicht sicher erkennen oder bestimmen, ob ein bestimmter Fehler bei einer Wiederholung auftrat.

---

[Zurück: Spend Proof: Kosten pro Erfolg](spend-proof.md) · [Weiter: Quality Gate: vor Änderungen vergleichen](quality-gate.md)
