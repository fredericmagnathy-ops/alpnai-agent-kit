# Ihr erstes Audit

Erstellen Sie ein vollständiges Beispiel, starten Sie die Berechnung und erhalten Sie ein erklärtes Ergebnis.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/quickstart.md) · [English](../en/quickstart.md) · [Deutsch](../de/quickstart.md)

## 1. Eine Beispieldatei erstellen

Das folgende Python-Skript erstellt audit.json mit 40 Aufgaben je Version, insgesamt 80 Versuchen. Alle Daten sind fiktiv. Beide Versionen lösen dieselben 39 Aufgaben erfolgreich.

Alternativ laden Sie die Demonstration im Werkzeug, ohne Python zu installieren.

```python
import json
from pathlib import Path

runs = []
for number in range(1, 41):
    task_id = f"demo-{number:03d}"
    for variant, cost, latency in [
        ("baseline", 0.04, 2200),
        ("candidate", 0.025, 1600),
    ]:
        runs.append({
            "task_id": task_id,
            "workflow": "invoice_fields",
            "variant": variant,
            "cost_usd": cost,
            "success": number != 40,
            "latency_ms": latency,
        })

audit = {"runs": runs, "config": {"maxP95LatencyMs": 3000}}
Path("audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
```

## 2. Aufzeichnungen analysieren

Öffnen Sie Spend Proof, laden Sie audit.json oder fügen Sie den Inhalt ein und starten Sie die Analyse. Nutzen Sie zunächst die Standardschwellen; das Beispiel ergänzt nur eine P95-Grenze von 3.000 ms.

Verwenden Sie für eigene Daten eine neutrale Aufgabenkennung, die baseline und candidate teilen. Jeder weitere Versuch erhält eine eigene Zeile.

## 3. Ergebnis lesen

Die Referenz kostet insgesamt 1,60 USD, die Variante 1,00 USD. Beide erreichen 39 Erfolge bei 40 Aufgaben. Das erfasste P95 beträgt 2.200 ms beziehungsweise 1.600 ms.

Für diese fiktiven Daten ist candidate_for_controlled_trial zu erwarten: ein Kandidat für einen kontrollierten Versuch, keine automatische Freigabe zur Bereitstellung.

## 4. Speichern und mit eigenen Daten wiederholen

Laden Sie JSON für weitere Anwendungen und HTML zum Lesen oder Drucken herunter. Kennzeichnen Sie das Beispiel weiterhin eindeutig als fiktiv.

Wiederholen Sie den Ablauf mit vollständigen Kosten und vorab festgelegten Erfolgskriterien. Die API-Seite erklärt die Automatisierung dieser kostenlosen Berechnung.

---

[Zurück: ALPNAI verstehen](introduction.md) · [Weiter: Spend Proof: Kosten pro Erfolg](spend-proof.md)
