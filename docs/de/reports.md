# Berichte und Exporte

Ein lesbarer Bericht für Ihr Team und strukturiertes JSON für Ihre Werkzeuge.

[Dokumentationsbibliothek](README.md) · [ALPNAI](https://alpnai.com/de/docs)

[Français](../fr/reports.md) · [English](../en/reports.md) · [Deutsch](../de/reports.md)

## Das richtige Format wählen

JSON bewahrt Kennzahlen, Prüfungen, Entscheidungen und Einstellungen in einem wiederverwendbaren Format. HTML stellt Ergebnisse zum Lesen, Teilen oder Drucken dar.

In den kostenlosen Browserwerkzeugen werden Dateien lokal aus denselben Berechnungen erzeugt. Projects ermöglicht zusätzlich den Download aggregierter Ergebnisse aus Ihrem Konto. Für diese Berichte ist kein Schreibdienst eines Sprachmodells erforderlich.

## Analyse herunterladen

Führen Sie zuerst eine gültige Analyse aus und nutzen Sie danach den JSON- oder HTML-Download des Moduls. Der Browser speichert die Datei auf Ihrem Gerät.

Für PDF öffnen Sie HTML, wählen Drucken und gegebenenfalls Als PDF speichern. Das PDF erstellt Ihr Browser, kein externer Konvertierungsdienst.

## Einen API-Bericht lesen

Die Spend-Proof-API liefert eine Hülle mit mode, payment_required, persisted und data. Der Bericht steht in data. Das Skript liest die mit dem Beispiel der API-Seite gespeicherte Antwort.

Es extrahiert den Bericht nach audit-report.json, ergänzt keinen generierten Kommentar und sendet keine Daten an andere Stellen.

```python
import json
from pathlib import Path

response = json.loads(Path("audit-response.json").read_text(encoding="utf-8"))
if response.get("error"):
    raise SystemExit(response["error"])
report = response["data"]
for item in report["workflows"]:
    print(item["workflow"], item["decision"])
    print(item["baseline"]["cost_per_successful_task_usd"])
    print(item["candidate"]["cost_per_successful_task_usd"])
Path("audit-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
```

## Ergebnisse nachvollziehbar halten

Bewahren Sie Datenherkunft und Testschwellen auf. Fiktive Beispiele müssen auch nach dem Export gekennzeichnet bleiben. Schützen Sie Berichte, wenn Kennungen Geschäftsinformationen erkennen lassen.

Lokale Exporte sind weder Rechnungen noch Zahlungsnachweise. Die kostenlosen Browserwerkzeuge speichern keinen Cloud-Verlauf: Laden Sie den Bericht vor dem Schliessen der Seite herunter. Um Analysen bewusst online zu speichern, nutzen Sie Projects mit Ihrem ChatGPT-Konto.

## Berichte in Projects speichern

Projects speichert aggregierte Ergebnisse, Projekt-/Versionsnamen und erforderliche Kennungen zur Nachverfolgung. Beim Speichern werden Messwerte zur Berechnung an den Server übertragen; Rohversuche und Prompts werden nicht in der Datenbank gespeichert. Eine lokale Analyse oder ein Aufruf einer kostenlosen Analyse-API erstellt nicht automatisch einen Projects-Bericht.

Der angemeldete Kontoinhaber kann bis zu zwei Berichte vergleichen und deren JSON oder einen druckbaren Bericht herunterladen. Bestehende Berichte bleiben nach Ablauf eines Abonnements herunterladbar. Löschen entfernt Inhalt und Bezeichnungen, ohne Kontingent wiederherzustellen; ein Fingerabdruck und technische Daten zur Nachverfolgung bleiben erhalten.

---

[Quality Gate: vor Änderungen vergleichen](quality-gate.md) · [HTTP-API](api.md)
