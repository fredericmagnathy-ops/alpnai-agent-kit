# AlpNAI-Integrationskit für Agenten

[English](README.md) · [Français](README.fr.md)

Einen autorisierten Agenten mit der **AlpNAI-Sandbox** verbinden und eine datierte Sammlung mit Quellenangaben prüfen. Dieses eigenständige Kit enthält einen Python-Client, MCP-Nachrichtenbeispiele und lokale Vertragstests. Es betreibt keinen Server, wickelt keine Kryptozahlungen ab, erstellt keine Wallet, verlängert kein Abonnement und kontaktiert keine potenziellen Kunden.

**Status: vorbereitete Pilotdateien; durch dieses Kit weder veröffentlicht noch aktiviert. Keine echten Zahlungen.** Standardadresse: [alpnai.frederic150452.chatgpt.site](https://alpnai.frederic150452.chatgpt.site/). Der Betreiber steuert die Sichtbarkeit der Website. Wenn ein Endpunkt eine ChatGPT-Anmeldeseite zurückgibt, kann dieser Client die API nicht direkt nutzen: Ein Agentenschlüssel umgeht den Plattformzugang nicht. Sobald verfügbar, die vom Betreiber dokumentierte zugängliche Bereitstellung verwenden. Das Kit übernimmt keine Browsersitzungen.

## Einstieg

Python 3.10 oder neuer; keine zusätzlichen Pakete erforderlich. Befehle in diesem Verzeichnis ausführen.

```sh
python3 examples/buy.py --catalog
python3 examples/buy.py --sample
```

Nach der Bereitstellung ist ein Pilotschlüssel unter [/start](https://alpnai.frederic150452.chatgpt.site/start) erhältlich; der Betreiber legt das verfügbare simulierte Budget fest. Der erste Kaufbefehl fragt den Schlüssel verdeckt ab. Für automatisierte Aufrufe `ALPNAI_AGENT_KEY` über die Geheimnisverwaltung des Prozesses bereitstellen. Schlüssel nicht in Quellcode, veröffentlichte Dateien oder Befehle mit Shell-Verlauf einfügen.

```sh
python3 examples/buy.py --product snapshot --max-usdc 0.01 --state .alpnai/snapshot-001.json
```

**Denselben Befehl** erneut ausführen, um denselben Kauf zu wiederholen. Die Statusdatei bewahrt die Kauf-ID auch nach einem Prozessneustart. Eine erfolgreiche Wiederholung sollte denselben Beleg mit `replayed: true` zurückgeben. Nach einer Zeitüberschreitung die Datei behalten. Eine andere Datei für Produkt, Datum oder Schlüssel nur verwenden, wenn tatsächlich ein neuer Kauf beabsichtigt ist.

```sh
python3 examples/buy.py --product changes --since 2026-06-01 --max-usdc 0.05 --state .alpnai/changes-001.json
python3 examples/buy.py --product evidence --max-usdc 0.25 --state .alpnai/evidence-001.json
```

Mit `ALPNAI_BASE_URL` oder `--base-url` eine vom Betreiber autorisierte HTTPS-Origin wählen. HTTP ist nur für lokale Loopback-Tests erlaubt. Der Client lehnt Weiterleitungen und unerwartete Produktpfade ab. Standard: 10 Sekunden pro Netzwerkoperation und höchstens 3 Kaufversuche. `--timeout` erlaubt höchstens 60 Sekunden, `--attempts` höchstens 4 Versuche. Nur vorübergehende Netzwerkfehler oder HTTP 429/500/502/503/504 lösen Wiederholungen aus, immer mit derselben Kauf-ID.

## Prüfungen und Grenzen

Vor dem Kauf lädt der Client den Katalog ohne Agentenschlüssel. Er verlangt `mode: sandbox`, `live_payments_enabled: false`, `currency: USDC` und `network: eip155:8453`. Er prüft Pfad, Preis, Übereinstimmung mit dem Betrag in Einheiten mit sechs Dezimalstellen und die lokale Grenze `--max-usdc`. Gespeichert werden Schlüssel-Hash, Parameter, Kauf-ID und Beleg, niemals der unverschlüsselte Schlüssel.

Die Grenze gilt für **einen logischen simulierten Kauf**, nicht für alle Statusdateien zusammen. Das gesamte Testbudget kontrolliert der Server separat. Der Katalogabruf reserviert keinen Preis atomar: Die API besitzt keinen serverseitigen Höchstpreisparameter. Eine Preisänderung zwischen zwei Aufrufen kann deshalb die simulierte Belastung beeinflussen. Der Client lehnt dann den abweichenden Beleg ab, behält die Statusdatei und stoppt. Das ist keine Absicherung für echte Zahlungen.

Ein gültiger Beleg muss `mode: sandbox`, `settled: false`, `real_revenue_usdc: 0`, den erwarteten `simulated_price_usdc`, eine Beleg-ID und ein Datenobjekt enthalten. Private Wallet-Schlüssel oder Wiederherstellungsphrasen werden nicht angefordert. USDC bezeichnet hier simulierte Beträge; es werden keine Token übertragen.

## Schnittstelle und Umfang

| Route | Aktueller Sandbox-Vertrag |
|---|---|
| `GET /api/v1/catalog` | Kostenlose Produktmetadaten und vorgeschlagene Preise |
| `GET /api/v1/sample` | Kostenloses datiertes Datenbeispiel mit Quellen |
| `GET /api/v1/snapshot` | 0,01 simulierte USDC |
| `GET /api/v1/changes?since=YYYY-MM-DD` | 0,05 simulierte USDC; Sammlungsereignisse nach dem Datum |
| `GET /api/v1/evidence` | 0,25 simulierte USDC; Belege und Methodik |
| `POST /mcp` | Streamable HTTP; [MCP-Hinweise auf Englisch](mcp/README.md) |

Kauf-Header: `Authorization: Bearer <test-key>`, `X-AlpNAI-Mode: sandbox`, `Idempotency-Key: <persisted-id>`. IDs enthalten 8–100 Buchstaben, Ziffern, Bindestriche oder Unterstriche. [Katalogbeispiel](examples/catalog.sample.json) und [OpenAPI-Kopie](openapi.snapshot.json) bilden den vorbereiteten Vertrag ab; sie bestätigen keinen öffentlichen Serverzugang. Die [Herkunftsdatei](contract-provenance.json) dokumentiert die Grundlage.

Die erste Sammlung ist auf den 14. September 2026 datiert und betrifft OpenAIs Mitteilung vom 8. Juni 2026 über die vertrauliche Einreichung eines S-1-Entwurfs. Sie ist begrenzt und kuratiert. Change Set filtert datierte Ereignisse dieser Sammlung; beliebige historische Versionen werden noch nicht verglichen. Nullwerte in IPO-Feldern beweisen nicht, dass es keine späteren Mitteilungen gibt. Quellenverweise stehen in den gelieferten Daten. AlpNAI ist unabhängig von OpenAI und verkauft weder Aktien noch Zuteilungen oder Anlageempfehlungen.

## Vorbereitete Cloud-Überwachung

Vorgesehenes Repository: [fredericmagnathy-ops/alpnai-agent-kit](https://github.com/fredericmagnathy-ops/alpnai-agent-kit). MCP-Namensraum: `io.github.fredericmagnathy-ops/alpnai`. Die Veröffentlichung erfolgt separat durch den Betreiber.

Zwei vorbereitete GitHub-Actions-Workflows prüfen Quellen alle sechs Stunden zur Minute 17 UTC sowie Katalog, Datenbeispiel und MCP täglich um 07:43 UTC. Nach Bereitstellung sind auch manuelle Starts möglich. Die Quellenprüfung protokolliert Ergebnisse, ändert keine Tatsachenaussagen und schlägt bei Prüfbedarf oder nicht erreichbaren Quellen fehl. Die Zustandsprüfung nutzt `server/discover` und `tools/list` mit MCP `2026-07-28`, ohne Kaufwerkzeuge aufzurufen.

Vor Aktivierung Endpunkt und autorisierte Geheimnisse konfigurieren, API bereitstellen und Workflows im Standardbranch ablegen. Berichte enthalten nur Status und Zähler, werden sieben Tage aufbewahrt und erscheinen als GitHub-Zusammenfassung. Fehlgeschlagene Läufe können abhängig von den Kontoeinstellungen GitHub-Benachrichtigungen auslösen. Zeitpläne können sich verzögern und garantieren keinen durchgehenden Betrieb. Englische Einrichtungsanleitung: [Cloud automation](CLOUD_AUTOMATION.md).

Der tägliche Workflow protokolliert ausserdem eine aggregierte Wachstumsdiagnose in einem separaten autorisierten Schritt. Die künftige Hauptdomain ist `https://alpnai.com`; `ALPNAI_BASE_URL` erst nach Anbindung und Prüfung der Domain umstellen.

## Lokal prüfen

```sh
python3 -m unittest discover -s tests -v
```

Die Tests verwenden ausschliesslich Simulationen im Speicher oder einen lokalen HTTP-Server mit synthetischen Daten. Sie prüfen eine verlorene Antwort nach simulierter Belastung, Wiederholungen, Preisgrenzen, Katalogkonsistenz, Modus, gespeicherte Parameter, Weiterleitungen, Anmeldeseiten und ungültige Belege. Cloud-Tests prüfen zusätzlich den Umgang mit Geheimnissen, aggregierte Berichte, erforderliche Quellenprüfungen und die MCP-Erkennung ohne Käufe. Sie bestätigen weder eine Produktionsbereitstellung noch finanzielle Tatsachen. Externe Konten werden nicht benötigt.

Bei 401/403 Zugang, Widerruf oder Budget prüfen. 409 bedeutet, dass dieselbe ID mit anderen Parametern verwendet wurde. Nach einem Absturz kann eine `.lock`-Datei zurückbleiben: Vor dem Entfernen nur dieser Sperrdatei sicherstellen, dass kein Client mehr läuft. Die Kaufstatusdatei behalten. Statusdateien und Belege gehören in das von Git ausgeschlossene Verzeichnis `.alpnai/`.

## Lizenz und Kontakt

Die [MIT-Lizenz](LICENSE) gilt nur für Python-Code. API-Daten, Quelldokumente, Marken und andere Inhalte fallen nicht darunter; dafür gelten die [Dienstbedingungen](https://alpnai.frederic150452.chatgpt.site/legal) und die Rechte der Originalquellen. Dieses Kit versendet keine Marketingnachrichten und veröffentlicht keine externen Einträge. Integrationskontakt: [frederic@alpnor.com](mailto:frederic@alpnor.com).
