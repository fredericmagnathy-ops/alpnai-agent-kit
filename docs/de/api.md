# HTTP-API

Senden Sie Aufzeichnungen per Skript und erhalten Sie dieselbe strukturierte Berechnung.

[Dokumentationsbibliothek](README.md) · [ALPNAI](https://alpnai.com/de/docs)

[Français](../fr/api.md) · [English](../en/api.md) · [Deutsch](../de/api.md)

## Einen Schlüssel erhalten

Öffnen Sie /start, melden Sie sich an und erstellen Sie den Testzugang. Kopieren Sie den vom Dienst erzeugten Schlüssel bei der Anzeige. alp_test_… beschreibt nur das Format.

Speichern Sie den Schlüssel in der Umgebungsvariablen ALPNAI_AGENT_KEY auf Ihrem Rechner oder Server. Eine Wallet-Adresse ersetzt diesen Schlüssel nicht.

## Ein Audit berechnen

Erstellen Sie audit.json mit der Kurzanleitung und führen Sie die Anfrage aus. POST /api/v1/spend-proof erwartet runs/config-JSON und einen aktiven Schlüssel. Für dieses kostenlose Audit ist kein Zahlungsheader erforderlich.

Das Beispiel speichert die Antwort als audit-response.json und liest den Schlüssel aus der Umgebung statt aus dem Quelltext.

```bash
curl --fail-with-body --silent --show-error \
  'https://alpnai.com/api/v1/spend-proof' \
  --header "Authorization: Bearer ${ALPNAI_AGENT_KEY}" \
  --header 'Content-Type: application/json' \
  --data-binary @audit.json \
  --output audit-response.json
```

## Vertrag und Datengröße

Grenzen: 1 bis 1.000 Versuche, höchstens 512.000 UTF-8-Bytes. Versuchskosten liegen zwischen 0 und 10.000 USD, Dauern zwischen 0 und 86.400.000 ms. Unbekannte Felder und falsche Datentypen werden abgewiesen.

Eine erfolgreiche Antwort enthält mode:"free_audit", payment_required:false, persisted:false und data. persisted:false bezeichnet das fehlende Speichern der Aufzeichnungen in der Anwendungsdatenbank, nicht die Löschung aller Infrastrukturprotokolle.

## Fehler behandeln

400 invalid_audit_input: JSON, Felder oder Grenzen korrigieren. 401 agent_key_required: Schlüssel und Aktivierung prüfen. 403 origin_forbidden: Browseranfragen anderer Ursprünge werden abgewiesen.

413 body_too_large: Datei verkleinern und vollständige Aufgabenpaare erhalten. 503 audit_unavailable: Verarbeitung fehlgeschlagen; nur begrenzt wiederholen. collect_more_data in einer 200-Antwort ist ein Analyseergebnis und kein HTTP-Ausfall.

## Weitere verfügbare Routen

Alle drei kostenlosen Berechnungen akzeptieren dasselbe JSON und denselben Schlüssel: POST /api/v1/spend-proof, POST /api/v1/latency und POST /api/v1/quality-gate. Ersetzen Sie im Beispiel nur den Pfad, um die Berechnung zu wählen.

Die latency-API liefert groups mit unter anderem p50_ms, p95_ms, max_ms und retry_attempts. quality-gate liefert workflows mit comparison, gates, decision und Erfolgsraten. GET /openapi.json beschreibt den Vertrag; GET /api/v1/catalog und GET /api/v1/sample sind öffentlich. HTML-Exporte werden weiterhin lokal erstellt.

## Ohne Konto direkt mit einem Agenten testen

GET /api/v1/performance-sample liefert synthetische Beispielmessungen sowie die tatsächlich berechneten Kosten-, Latenz- und Qualitätsergebnisse. Dafür sind kein Konto, keine Wallet und keine Zahlung nötig.

REST-Katalog und MCP get_catalog beschreiben dieselben Analysen, Eingaben, Ergebnisse, Preise und Zugriffsanforderungen. Aktivieren Sie einmal einen Schlüssel für eigene Messungen; danach kann Ihr Agent die Werkzeuge ohne Eingriff des ALPNAI-Betreibers aufrufen.

verify-performance-sample.mjs im Kit lädt Katalog und Beispiel, berechnet die Werte erneut und liefert PASS oder FAIL. Es erfolgt kein Kauf. Dieser Test bestätigt Beispiel und Berechnung, keine Kryptowährungsabrechnung.

```
GET https://alpnai.com/api/v1/catalog
GET https://alpnai.com/api/v1/performance-sample
```

---

[Berichte und Exporte](reports.md) · [Einen Agenten über MCP verbinden](mcp.md)
