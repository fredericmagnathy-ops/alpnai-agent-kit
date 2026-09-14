# Berichte und Exporte

Ein lesbarer Bericht für Ihr Team und strukturiertes JSON für Ihre Werkzeuge.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/reports.md) · [English](../en/reports.md) · [Deutsch](../de/reports.md)

## Das richtige Format wählen

JSON bewahrt Kennzahlen, Prüfungen, Entscheidungen und Einstellungen in einem wiederverwendbaren Format. HTML stellt Ergebnisse zum Lesen, Teilen oder Drucken dar.

Die Dateien werden lokal aus denselben Berechnungen erzeugt. Für den Bericht ist kein Schreibdienst eines Sprachmodells erforderlich.

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

Lokale Exporte sind weder Rechnungen noch Zahlungsnachweise. Die Seite bietet keinen Cloud-Verlauf der Audits. Speichern Sie den Bericht vor dem Schließen.

---

[Zurück: Quality Gate: vor Änderungen vergleichen](quality-gate.md) · [Weiter: HTTP-API](api.md)
