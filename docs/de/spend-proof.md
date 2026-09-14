# Spend Proof: Kosten pro Erfolg

Berücksichtigen Sie Fehler und Wiederholungen beim Kostenvergleich erfasster Ergebnisse.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/spend-proof.md) · [English](../en/spend-proof.md) · [Deutsch](../de/spend-proof.md)

## Das Datenformat

Jede Zeile ist ein Versuch. task_id, workflow, variant, cost_usd und success sind Pflichtfelder; latency_ms ist optional. Feldnamen bleiben in allen Sprachen englisch.

Das Beispiel mit zwei Zeilen zeigt das Format. Für einen Vergleich sind standardmäßig 30 unterschiedliche Aufgaben je Version erforderlich.

```json
{
  "runs": [
    {
      "task_id": "task-01",
      "workflow": "invoice_fields",
      "variant": "baseline",
      "cost_usd": 0.04,
      "success": true,
      "latency_ms": 2200
    },
    {
      "task_id": "task-01",
      "workflow": "invoice_fields",
      "variant": "candidate",
      "cost_usd": 0.025,
      "success": true,
      "latency_ms": 1600
    }
  ]
}
```

## Welche Kosten dazugehören

Berücksichtigen Sie Kosten für Modell, Werkzeuge, Recherche und weitere Aufrufe des Versuchs. Erfassen Sie auch fehlgeschlagene Versuche. Rechnen Sie alle Werte vor dem Import in USD um.

cost_usd erlaubt höchstens sechs Nachkommastellen. Fassen Sie feinere Kosten vorher korrekt zusammen. Eine Zeichenfolge wie "0.04" ist keine Zahl und wird abgewiesen.

## So werden die Kosten berechnet

Versuche werden nach workflow, variant und task_id gruppiert. Eine Aufgabe gilt als erfolgreich, wenn mindestens ein erfasster Versuch success:true enthält. Sämtliche Kosten werden gezählt.

Kosten pro erfolgreicher Aufgabe = Gesamtkosten aller Versuche ÷ erfolgreiche Aufgaben. Ohne Erfolg ist das Ergebnis null; ein endlicher Wert kann nicht berechnet werden.

## Eine vergleichbare Monatsprojektion

monthlyTasks bezeichnet die monatlich von der Referenz gestarteten Aufgaben. Es gilt nur für einen einzelnen Workflow. Die Projektion vergleicht dieselbe erwartete Anzahl erfolgreicher Ergebnisse.

Sie erscheint nur für Kandidaten eines kontrollierten Versuchs. Integration, Migration, Bewertung und wirtschaftliche Fehlerfolgen sind nicht enthalten. realized_savings_usd bleibt null: Eine Projektion ist keine realisierte Einsparung.

## Einen aussagekräftigen Vergleich vorbereiten

Verwenden Sie exakt dieselben task_id-Werte und dieselbe Erfolgsdefinition für beide Varianten. Eine task_id darf nicht mehreren Workflows angehören. Trennen Sie Umgebungen und Testsätze vor dem Export.

Doppelte Zeilen zählen als weitere Versuche. Entfernen Sie Telemetrieduplikate vorher. Die Berechnung erkennt keine fehlenden Rechnungen und beweist nicht die Repräsentativität Ihrer Stichprobe.

---

[Zurück: Ihr erstes Audit](quickstart.md) · [Weiter: Latency Lab: Zeiten und Wiederholungen](latency.md)
