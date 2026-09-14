# ALPNAI-Dokumentation

Von Aufzeichnungen zu einer nachvollziehbaren Entscheidung.

[Dokumentation auf der Website](https://alpnai.com/de/docs) · [Integrationskit](../../README.de.md)

[Français](../fr/README.md) · [English](../en/README.md) · [Deutsch](../de/README.md)

Die Dokumentation beschreibt kostenlose Berechnungen und den Piloten. Sie behauptet weder einen Verzeichniseintrag noch einen echten Verkauf oder erfolgreichen Bankumtausch.

## Kostenlose Werkzeuge

[Spend Proof](https://alpnai.com/de/tools/spend-proof) · [Latency Lab](https://alpnai.com/de/tools/latency-lab) · [Quality Gate](https://alpnai.com/de/tools/quality-gate)

Alle drei Werkzeuge akzeptieren dieselben Aufzeichnungen. Browserberechnung und HTML/JSON-Exporte erfolgen lokal; API/MCP-Aufrufe senden die Daten mit aktivem Schlüssel zum Server. Der vorhandene Python-Auditclient bleibt auf Spend Proof beschränkt.

## Erste Schritte

| Seite | Nutzen |
|---|---|
| [ALPNAI verstehen](introduction.md) | Vergleichen Sie Agenten anhand von Kosten, erfassten Zeiten und Erfolg bei denselben Aufgaben. |
| [Ihr erstes Audit](quickstart.md) | Erstellen Sie ein vollständiges Beispiel, starten Sie die Berechnung und erhalten Sie ein erklärtes Ergebnis. |

## Werkzeuge

| Seite | Nutzen |
|---|---|
| [Spend Proof: Kosten pro Erfolg](spend-proof.md) | Berücksichtigen Sie Fehler und Wiederholungen beim Kostenvergleich erfasster Ergebnisse. |
| [Latency Lab: Zeiten und Wiederholungen](latency.md) | Erkennen Sie langsame Aufgaben und messen Sie zusätzliche Versuche anhand derselben Aufzeichnungen. |
| [Quality Gate: vor Änderungen vergleichen](quality-gate.md) | Prüfen Sie Erfolg, Kosten und Latenz, bevor Sie eine Variante übernehmen. |
| [Berichte und Exporte](reports.md) | Ein lesbarer Bericht für Ihr Team und strukturiertes JSON für Ihre Werkzeuge. |

## Integrationen

| Seite | Nutzen |
|---|---|
| [HTTP-API](api.md) | Senden Sie Aufzeichnungen per Skript und erhalten Sie dieselbe strukturierte Berechnung. |
| [Einen Agenten über MCP verbinden](mcp.md) | Entdecken Sie Werkzeuge und rufen Sie audit_agent_costs mit Ihren Aufzeichnungen auf. |

## Vertrauen

| Seite | Nutzen |
|---|---|
| [Zahlungen und Testmodus](payments.md) | Unterscheiden Sie kostenlose Audits, simulierte Käufe und x402-Zahlungen in der Validierung. |
| [Daten und Zugänge](security.md) | Bereiten Sie minimale Aufzeichnungen vor und wählen Sie den Berechnungsort. |

## Kostenlose APIs

| POST | Werkzeug |
|---|---|
| `/api/v1/spend-proof` | Spend Proof |
| `/api/v1/latency` | Latency Lab |
| `/api/v1/quality-gate` | Quality Gate |

[Acht MCP-Werkzeuge](mcp.md)

MCP-Kaufbeispiele bleiben im Sandbox-Modus. PayAI/x402 wird validiert; dieses Repository belegt keine Mainnet-Abwicklung. Das Kit führt keine Abonnements, Provisionen oder automatischen Banküberweisungen aus.
