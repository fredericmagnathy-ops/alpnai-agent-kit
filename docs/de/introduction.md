# ALPNAI verstehen

Vergleichen Sie Agenten anhand von Kosten, erfassten Zeiten und Erfolg bei denselben Aufgaben.

[Dokumentationsbibliothek](README.md) · [ALPNAI](https://alpnai.com/de/docs)

[Français](../fr/introduction.md) · [English](../en/introduction.md) · [Deutsch](../de/introduction.md)

## Die entscheidende Frage

Ein Agent kann pro Aufruf günstiger, pro Ergebnis aber teurer werden, wenn er erneut versucht oder scheitert. ALPNAI fasst erfasste Versuche nach Aufgabe zusammen.

Vergleichen Sie eine Referenz, baseline, mit einer Variante, candidate. Das Ergebnis hilft bei der Wahl des nächsten Tests.

## Das passende Werkzeug wählen

Spend Proof vergleicht die Kosten pro erfolgreicher Aufgabe. Latency Lab untersucht P50, P95 und erfasste Wiederholungen. Quality Gate prüft Schwellen vor einem begrenzten Versuch.

Alle drei Ansichten verwenden dasselbe Datenformat. Laden Sie JSON für einen Agenten und einen lesbaren HTML-Bericht für Ihr Team herunter.

## Ein einfacher Ablauf

Verwenden Sie dieselben Aufgabenkennungen für beide Versionen. Importieren Sie vollständige Kosten, Ihre Erfolgskennzeichnungen und gegebenenfalls Zeiten. Analysieren, prüfen und speichern Sie den Bericht.

Die Browserberechnung benötigt kein Konto. API und MCP benötigen einen aktiven ALPNAI-Schlüssel; das Audit bleibt kostenlos.

Projects ergänzt einen privaten Verlauf und Vergleiche gespeicherter Berichte. Melden Sie sich mit ChatGPT an, um drei kostenlose Berichte zu nutzen oder ein Stripe-Abonnement zu wählen. Dieser Bereich ist von den kostenlosen APIs/MCP und Kryptokäufen im Testmodus getrennt.

## Was die Messung aussagt

Ergebnisse beschreiben die bereitgestellten Daten. ALPNAI ersetzt weder Ihre Definition eines guten Ergebnisses noch verändert es Ihre Agenten. Eine geeignete Variante muss in Ihrer Umgebung erprobt werden.

Die Evidence-Dienste zum OpenAI-Börsengang sind ein gesonderter Pilot. Testkäufe und fiktive Budgets sind keine Umsätze oder Geldanlagen.

## Ohne Konto direkt mit einem Agenten testen

GET /api/v1/performance-sample liefert synthetische Beispielmessungen sowie die tatsächlich berechneten Kosten-, Latenz- und Qualitätsergebnisse. Dafür sind kein Konto, keine Wallet und keine Zahlung nötig.

REST-Katalog und MCP get_catalog beschreiben dieselben Analysen, Eingaben, Ergebnisse, Preise und Zugriffsanforderungen. Aktivieren Sie einmal einen Schlüssel für eigene Messungen; danach kann Ihr Agent die Werkzeuge ohne Eingriff des ALPNAI-Betreibers aufrufen.

verify-performance-sample.mjs im Kit lädt Katalog und Beispiel, berechnet die Werte erneut und liefert PASS oder FAIL. Es erfolgt kein Kauf. Dieser Test bestätigt Beispiel und Berechnung, keine Kryptowährungsabrechnung.

```
GET https://alpnai.com/api/v1/catalog
GET https://alpnai.com/api/v1/performance-sample
```

---

[Ihr erstes Audit](quickstart.md)
