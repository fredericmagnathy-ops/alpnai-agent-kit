# ALPNAI-Integrationskit für Agenten

## TypeScript-Kaufintegration

Der [x402-Kaufclient](clients/x402-buyer/README.md) ist als Quellcode mit englischer Integrationsanleitung verfügbar. Er setzt eine bestehende Autorisierung des Inhabers, ein geeignetes Rechnungsprofil und einen Wallet-Adapter voraus. Er prüft das konkrete Angebot, behält dieselbe Kaufkennung und setzt die Auftragsabfrage nach einem Neustart fort. **Offline geprüft; die echte ALPNAI-Zahlungsannahme ist weiterhin geschlossen.** Er eröffnet kein Konto und erhöht kein Budget. Das folgende Python-Kaufbeispiel bleibt auf den Testmodus beschränkt.

Angebote ohne Schlüssel prüfen: [Snapshot](https://alpnai.com/api/v1/offers/snapshot), [Change Set](https://alpnai.com/api/v1/offers/changes), [Evidence Pack](https://alpnai.com/api/v1/offers/evidence). Die öffentlichen Beschreibungen enthalten Katalogpreis, Zugangsvoraussetzungen, Liefervertrag und Verfügbarkeit. Sie sind keine zahlbaren x402-Angebote. Authentifizierungsfehler enthalten `offer_url` und einen `describedby`-Link zur Beschreibung.

Der native MCP-x402-Transport ist implementiert: signierte Zahlungen verwenden params._meta["x402/payment"], bestätigte Belege result._meta["x402/payment-response"]. Siehe [MCP-Anleitung](docs/de/mcp.md). USDC-Zahlungen bleiben laut öffentlichem Katalog deaktiviert; das Transport-Update ist keine Verkaufsfreigabe. Das Kaufskript bleibt auf Sandbox-Tests beschränkt.

Sie haben einen CSV-Export? [Importieren Sie Ihre eigenen Versuche](onboarding/README.de.md) vor dem ersten Audit.

[English](README.md) · [Français](README.fr.md)

ALPNAI bietet autorisierten KI-Agenten deterministische Analysen von **Kosten, Latenz und Qualität**. Vergleichen Sie Varianten anhand derselben aufgezeichneten Aufgaben und speichern Sie berechnete Berichte in einem vom Inhaber freigegebenen Projekt. Prüfen Sie zuerst das öffentliche Beispiel, bevor Sie eigene Daten anbinden.

## Mit zwei GET-Anfragen prüfen

Führen Sie den eigenständigen Prüfer im Repository-Verzeichnis mit **Node.js 18 oder neuer** aus. Zusätzliche Pakete, ein Konto, ein API-Schlüssel oder eine Wallet sind nicht erforderlich.

```sh
node examples/verify-performance-sample.mjs
```

Er liest `GET /api/v1/catalog` und `GET /api/v1/performance-sample`, berechnet Kosten, Erfolgszahlen und das aufgezeichnete P95 des Beispiels unabhängig nach und gibt `PASS` oder `FAIL` aus. Er folgt keinen Weiterleitungen, übermittelt keine Zugangsdaten und führt weder POST-Anfragen, Käufe noch Dateischreibvorgänge aus. Die Daten sind synthetisch: Das Ergebnis belegt reproduzierbare Berechnungen, keine Kundeneinsparung oder Zahlungsabwicklung.

Ein autonomer Client kann denselben [öffentlichen Katalog](https://alpnai.com/api/v1/catalog) und dasselbe [Leistungsbeispiel](https://alpnai.com/api/v1/performance-sample) lesen. Der Katalog beschreibt drei kostenlose Analysen, erforderliche Berechtigungen und die autorisierte Berichtszustellung; das MCP-Werkzeug `get_catalog` liefert denselben Vertrag. Die [OpenAPI-Kopie](openapi.snapshot.json) enthält detaillierte Eingabe- und Ausgabeschemas. Das separate MCP-Werkzeug `get_free_sample` liefert datierte Quellenbelege, nicht dieses Leistungsbeispiel.

Für eigene Messdaten aktiviert der Inhaber einmal einen Agentenschlüssel über [/start](https://alpnai.com/start). Danach kann der Agent die kostenlosen Analysen innerhalb seiner Berechtigungen aufrufen. Die Speicherung in Projects erfordert zusätzlich eine ausdrückliche Freigabe. Ein Schlüssel berechtigt weder zu Käufen noch zu Tarifwechseln oder Produktivänderungen. [MCP-Anbindung](docs/de/mcp.md) · [Berichtszustellung](docs/de/projects-automation.md).

**Status: öffentlicher Dienst unter [alpnai.com](https://alpnai.com/); API-/MCP-Kryptokäufe bleiben ausschließlich in der Sandbox.** Der primäre MCP-Endpunkt ist `/api/mcp`. Einen aktiven Pilotschlüssel erhalten Sie über [/start](https://alpnai.com/start). Agentenschlüssel umgehen keine Kontoberechtigungen; das Kit übernimmt keine Browsersitzungen.

## ALPNAI Projects

Nach Freigabe durch den Inhaber in Projects kann ein Agent Berichte mit `save_project_report` (MCP) oder dem Python-Client `examples/save_project.py` automatisch zustellen. Manuelle und automatische Speicherungen teilen sich dasselbe Kontingent. [Einrichtung](docs/de/projects-automation.md).

Ergebnisse Ihrer Agenten privat speichern und vergleichen. [Projects öffnen](https://alpnai.com/projects), **mit ChatGPT anmelden**: 3 gespeicherte Berichte kostenlos, ohne Karte. Kostenpflichtige Angebote: **19 CHF, 19 EUR, 19 USD oder 19 GBP monatlich** für 100 neue Berichte je bezahlter Monatsperiode oder **190 CHF, 190 EUR, 190 USD oder 190 GBP jährlich** für 1.200 je bezahlter Jahresperiode; 10 Projekte. Dies sind feste lokale Preise ohne Währungsumrechnung. Stripe verwaltet das separate Website-Abonnement. Seine Verfügbarkeit wird in Projects angezeigt; Zugang setzt bestätigte Zahlung voraus. Das Kit schließt keine Abonnements ab und überträgt keine Kryptowährung.

[Projects-Leitfaden](docs/de/projects.md) · [Bedingungen](https://alpnai.com/de/legal/projects) · [Datenschutz](https://alpnai.com/de/legal/privacy)

## Dokumentationsbibliothek

[Dokumentation auf der Website](https://alpnai.com/de/docs) · [Zwölf praktische Anleitungen](docs/de/README.md)

[FR](https://alpnai.com/fr/docs) · [EN](https://alpnai.com/en/docs) · [DE](https://alpnai.com/de/docs)

[Spend Proof](https://alpnai.com/de/tools/spend-proof) · [Latency Lab](https://alpnai.com/tools/latency-lab) · [Quality Gate](https://alpnai.com/tools/quality-gate)

Alle drei Werkzeuge akzeptieren dieselben Aufzeichnungen. Browserberechnung und HTML/JSON-Exporte erfolgen lokal; API/MCP-Aufrufe senden die Daten mit aktivem Schlüssel zum Server. Der vorhandene Python-Auditclient bleibt auf Spend Proof beschränkt.

| Werkzeug | Kostenlose APIs | MCP |
|---|---|---|
| Spend Proof | `POST /api/v1/spend-proof` | `audit_agent_costs` |
| Latency Lab | `POST /api/v1/latency` | `analyze_agent_latency` |
| Quality Gate | `POST /api/v1/quality-gate` | `check_agent_quality` |

[Zehn MCP-Werkzeuge](docs/de/mcp.md): `get_catalog`, `get_free_sample`, `audit_agent_costs`, `analyze_agent_latency`, `check_agent_quality`, `save_project_report`, `get_order`, `purchase_snapshot`, `purchase_changes`, `purchase_evidence`.

MCP-Kaufbeispiele bleiben im Sandbox-Modus. PayAI/x402 wird validiert; dieses Repository belegt keine Mainnet-Abwicklung. Das Kit führt keine Abonnements, Provisionen oder automatischen Banküberweisungen aus.

## Kostenloser Spend-Proof-Audit

Stellen Sie `ALPNAI_AGENT_KEY` über die Geheimnisverwaltung Ihres Prozesses bereit. Wählen Sie einen privaten Export und eine neue lokale Berichtsdatei. Die mitgelieferte Datei enthält **fiktive Demonstrationsdaten**, keine Kundeneinsparungen.

```sh
python3 examples/audit.py --input examples/spend-proof.synthetic.json --report reports/mein-audit.json
```

Erstellen Sie zuerst das lokale Verzeichnis `reports/` oder wählen Sie ein anderes vorhandenes privates Verzeichnis. Der Bericht wird mit eingeschränkten Berechtigungen gespeichert und nie im Terminal ausgegeben. Bestehende Dateien werden nicht überschrieben. `POST /api/v1/spend-proof` ist mit aktivem Bearer-Schlüssel kostenlos: keine Zahlung, keine Belastung des Testbudgets, keine Anbieteranbindung und keine Berichtsspeicherung durch den Dienst. Prompts, Antworten, Kundendokumente und Geheimnisse gehören nicht in die Eingabedaten.

Jede Zeile ist ein Versuch mit `task_id`, `workflow`, `variant` (`baseline` oder `candidate`), `cost_usd`, `success` und optional `latency_ms`. Erfassen Sie Kosten für Modelle, Werkzeuge und Wiederholungen. Höchstens 1 000 Zeilen und 512 000 UTF-8-Bytes; Geldbeträge mit maximal sechs Nachkommastellen. Übereinstimmende Aufgabenkennungen, ausreichende Stichproben und geeignete Erfolgsquoten sind Voraussetzungen für eine bedingte Projektion. `monthlyTasks` bezeichnet gestartete Referenzaufgaben; die Kosten werden auf dieselbe erwartete Anzahl erfolgreicher Ergebnisse normiert. Unbekannte Versuchsverzerrungen schliessen eine automatische Produktivsetzung aus. Der Client verweigert Weiterleitungen, protokolliert keine Eingaben oder rohen Fehlermeldungen und wiederholt Anfragen nicht automatisch.

Der Audit analysiert bereitgestellte Ausführungsdaten. Kostenpflichtige laufende Überwachung, Umsatzzuordnung und automatisches Modellrouting sind über das Kit nicht verfügbar. Die nachfolgenden Datenkäufe bleiben simuliert.

## Beispiele für die Evidence-Sandbox

Python 3.10 oder neuer; keine zusätzlichen Pakete erforderlich. Befehle in diesem Verzeichnis ausführen.

```sh
python3 examples/buy.py --catalog
python3 examples/buy.py --sample
```

Ein Pilotschlüssel ist unter [/start](https://alpnai.com/start) erhältlich; der Betreiber legt das verfügbare simulierte Budget fest. Der erste Kaufbefehl fragt den Schlüssel verdeckt ab. Für automatisierte Aufrufe `ALPNAI_AGENT_KEY` über die Geheimnisverwaltung des Prozesses bereitstellen. Schlüssel nicht in Quellcode, veröffentlichte Dateien oder Befehle mit Shell-Verlauf einfügen.

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
| `GET /api/v1/performance-sample` | Öffentliche synthetische Messdaten und berechnete Ergebnisse; ohne Konto oder Zahlung |
| `GET /api/v1/sample` | Kostenloses datiertes Datenbeispiel mit Quellen |
| `GET /api/v1/snapshot` | 0,01 simulierte USDC |
| `GET /api/v1/changes?since=YYYY-MM-DD` | 0,05 simulierte USDC; Sammlungsereignisse nach dem Datum |
| `GET /api/v1/evidence` | 0,25 simulierte USDC; Belege und Methodik |
| `POST /api/v1/spend-proof` | Kostenloser Audit mit aktivem Bearer-Schlüssel; keine Zahlung oder Berichtsspeicherung durch den Dienst |
| `POST /api/v1/latency` | Kostenlose P50/P95-, Abdeckungs- und Wiederholungsanalyse; aktiver Schlüssel |
| `POST /api/v1/quality-gate` | Kostenlose Vergleichs- und Erfolgsprüfungen; aktiver Schlüssel |
| `POST /api/mcp` | Streamable HTTP; [MCP-Hinweise auf Englisch](mcp/README.md) |

Kauf-Header: `Authorization: Bearer <test-key>`, `X-ALPNAI-Mode: sandbox`, `Idempotency-Key: <persisted-id>`. IDs enthalten 8–100 Buchstaben, Ziffern, Bindestriche oder Unterstriche. [Katalogbeispiel](examples/catalog.sample.json) und [OpenAPI-Kopie](openapi.snapshot.json) bilden den vorbereiteten Vertrag ab; sie sind keine Messung der aktuellen Verfügbarkeit. Die [Herkunftsdatei](contract-provenance.json) dokumentiert die Grundlage.

Die erste Sammlung ist auf den 14. September 2026 datiert und betrifft OpenAIs Mitteilung vom 8. Juni 2026 über die vertrauliche Einreichung eines S-1-Entwurfs. Sie ist begrenzt und kuratiert. Change Set filtert datierte Ereignisse dieser Sammlung; beliebige historische Versionen werden noch nicht verglichen. Nullwerte in IPO-Feldern beweisen nicht, dass es keine späteren Mitteilungen gibt. Quellenverweise stehen in den gelieferten Daten. ALPNAI ist unabhängig von OpenAI und verkauft weder Aktien noch Zuteilungen oder Anlageempfehlungen.

## Vorbereitete Cloud-Überwachung

Öffentliches Repository: [fredericmagnathy-ops/alpnai-agent-kit](https://github.com/fredericmagnathy-ops/alpnai-agent-kit). MCP-Namensraum: `io.github.fredericmagnathy-ops/alpnai`. Diese Revision ist offline geprüft; aktuelle Cloud-Ergebnisse stehen in GitHub Actions.

Drei vorbereitete GitHub-Actions-Workflows prüfen Quellen alle sechs Stunden zur Minute 17 UTC, Katalog, Datenbeispiel und zehn MCP-Werkzeuge täglich um 07:43 UTC sowie bestehende Zahlungsaufträge zu den Minuten 06, 16, 26, 36, 46 und 56 jeder Stunde. Der Zahlungsabgleich liest die Blockchain und kann bestehende Buchungen aktualisieren; er sendet keine Zahlung, Abwicklung oder Banküberweisung. Exportiert werden nur die Anzahlen geprüfter, bestätigter und nicht bestätigter Aufträge in Gruppen von höchstens fünf. Nach Bereitstellung sind auch manuelle Starts möglich. Die Quellenprüfung protokolliert Ergebnisse, ändert keine Tatsachenaussagen und schlägt bei Prüfbedarf oder nicht erreichbaren Quellen fehl. Die Zustandsprüfung nutzt `server/discover` und `tools/list` mit MCP `2026-07-28`, ohne Kaufwerkzeuge aufzurufen.

Vor Aktivierung Endpunkt und autorisierte Geheimnisse konfigurieren, API bereitstellen und Workflows im Standardbranch ablegen. Berichte enthalten nur Status und Zähler, werden sieben Tage aufbewahrt und erscheinen als GitHub-Zusammenfassung. Fehlgeschlagene Läufe können abhängig von den Kontoeinstellungen GitHub-Benachrichtigungen auslösen. Zeitpläne können sich verzögern und garantieren keinen durchgehenden Betrieb. Englische Einrichtungsanleitung: [Cloud automation](CLOUD_AUTOMATION.md).

Der tägliche Workflow protokolliert ausserdem eine aggregierte Wachstumsdiagnose in einem separaten autorisierten Schritt. Die aktive Hauptdomain ist `https://alpnai.com`; verwenden Sie diese direkte Adresse in `ALPNAI_BASE_URL`.

## Lokal prüfen

```sh
python3 -m unittest discover -s tests -v
node --test tests/performance-sample.test.mjs
```

Die Tests verwenden ausschliesslich Simulationen im Speicher oder einen lokalen HTTP-Server mit synthetischen Daten. Sie prüfen eine verlorene Antwort nach simulierter Belastung, Wiederholungen, Preisgrenzen, Katalogkonsistenz, Modus, gespeicherte Parameter, Weiterleitungen, Anmeldeseiten und ungültige Belege. Cloud-Tests prüfen zusätzlich den Umgang mit Geheimnissen, aggregierte Berichte, erforderliche Quellenprüfungen und die MCP-Erkennung ohne Käufe. Sie bestätigen weder eine Produktionsbereitstellung noch finanzielle Tatsachen. Externe Konten werden nicht benötigt.

Bei 401/403 Zugang, Widerruf oder Budget prüfen. 409 bedeutet, dass dieselbe ID mit anderen Parametern verwendet wurde. Nach einem Absturz kann eine `.lock`-Datei zurückbleiben: Vor dem Entfernen nur dieser Sperrdatei sicherstellen, dass kein Client mehr läuft. Die Kaufstatusdatei behalten. Statusdateien und Belege gehören in das von Git ausgeschlossene Verzeichnis `.alpnai/`.

## Lizenz und Kontakt

Die [MIT-Lizenz](LICENSE) gilt nur für Python-Code. API-Daten, Quelldokumente, Marken und andere Inhalte fallen nicht darunter; dafür gelten die [Dienstbedingungen](https://alpnai.com/legal) und die Rechte der Originalquellen. Dieses Kit versendet keine Marketingnachrichten und veröffentlicht keine externen Einträge. Integrationskontakt: [frederic@alpnor.com](mailto:frederic@alpnor.com).
