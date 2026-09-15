# Einen Agenten über MCP verbinden

Entdecken Sie Werkzeuge und rufen Sie audit_agent_costs mit Ihren Aufzeichnungen auf.

## Endpunkt und Protokoll

Verwenden Sie POST https://alpnai.com/api/mcp. Der Server unterstützt MCP 2026-07-28 mit server/discover und JSON-Antworten. Er akzeptiert außerdem MCP-Clients der Versionen 2025-11-25, 2025-06-18 und 2025-03-26 über initialize.

Jede Anfrage enthält Protokollversion, Clientinformationen und Fähigkeiten unter params._meta. Technische Feldnamen werden nicht übersetzt.

## Ältere MCP-Clients

Clients von 2025 verwenden initialize, notifications/initialized, dann tools/list und tools/call. Konfigurieren Sie Streamable HTTP, akzeptieren Sie application/json und text/event-stream und senden Sie den Schlüssel als Authorization: Bearer. Der Transport ist zustandslos; dieselben Schlüssel- und Budgetprüfungen gelten. Das folgende Beispiel verwendet das Protokoll von 2026.

## Registrierte Werkzeuge

get_catalog und get_free_sample dienen zur Erkundung des Piloten. audit_agent_costs, analyze_agent_latency und check_agent_quality führen Spend Proof, Latency Lab beziehungsweise Quality Gate mit aktivem Schlüssel kostenlos aus. Alle drei akzeptieren runs und config.

purchase_snapshot, purchase_changes und purchase_evidence simulieren Evidence-Käufe mit fiktivem Budget. Sie benötigen idempotency_key; purchase_changes akzeptiert zusätzlich since im Format YYYY-MM-DD. Der Server stellt damit neun Werkzeuge bereit.

save_project_report berechnet und speichert einen Bericht im ausdrücklich vom Inhaber freigegebenen Projekt mit dem bestehenden Projects-Kontingent. Es benötigt request_id, title und input. Anleitung: https://alpnai.com/de/docs/projects-automation.

## Erkennen und das Audit aufrufen

Dieses Python-Skript nutzt nur die Standardbibliothek. Bereiten Sie audit.json und ALPNAI_AGENT_KEY wie auf der API-Seite vor. Es erkennt den Server, listet Werkzeuge und ruft das kostenlose Audit auf.

Die Header Mcp-Method und Mcp-Name entsprechen Methode und Werkzeugname. structuredContent enthält den Bericht ohne die data-Hülle der HTTP-API.

```python
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

meta = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "alpnai-docs", "version": "1.0.0"},
    "io.modelcontextprotocol/clientCapabilities": {},
}

def rpc(request_id, method, params):
    params = {**params, "_meta": meta}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2026-07-28",
        "Mcp-Method": method,
    }
    if method == "tools/call":
        headers["Mcp-Name"] = params["name"]
        headers["Authorization"] = "Bearer " + os.environ["ALPNAI_AGENT_KEY"]
    body = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
    request = Request("https://alpnai.com/api/mcp", data=body.encode(), headers=headers)
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(result["error"])
    if result["result"].get("isError"):
        raise RuntimeError(result["result"].get("content"))
    return result["result"]

print(rpc(1, "server/discover", {}))
print(rpc(2, "tools/list", {}))
audit = json.loads(Path("audit.json").read_text(encoding="utf-8"))
report = rpc(3, "tools/call", {"name": "audit_agent_costs", "arguments": audit})
print(json.dumps(report["structuredContent"], indent=2))
```

## Ergebnisse im Agenten verarbeiten

Prüfen Sie JSON-RPC-Fehler und result.isError, bevor Sie den Bericht lesen. Eine HTTP-Antwort beweist keinen erfolgreichen Werkzeugaufruf. Prüfen Sie danach decision und gates je Workflow.

Trennen Sie Aktionen vom Lesen des Berichts. Ein ALPNAI-Schlüssel und eine Versuchsempfehlung erteilen dem Agenten keinen Auftrag für Ausgaben oder Bereitstellungen.

## Ohne Konto direkt mit einem Agenten testen

GET /api/v1/performance-sample liefert synthetische Beispielmessungen sowie die tatsächlich berechneten Kosten-, Latenz- und Qualitätsergebnisse. Dafür sind kein Konto, keine Wallet und keine Zahlung nötig.

REST-Katalog und MCP get_catalog beschreiben dieselben Analysen, Eingaben, Ergebnisse, Preise und Zugriffsanforderungen. Aktivieren Sie einmal einen Schlüssel für eigene Messungen; danach kann Ihr Agent die Werkzeuge ohne Eingriff des ALPNAI-Betreibers aufrufen.

verify-performance-sample.mjs im Kit lädt Katalog und Beispiel, berechnet die Werte erneut und liefert PASS oder FAIL. Es erfolgt kein Kauf. Dieser Test bestätigt Beispiel und Berechnung, keine Kryptowährungsabrechnung.

```
GET https://alpnai.com/api/v1/catalog
GET https://alpnai.com/api/v1/performance-sample
```

## Einen Kauf über MCP anfordern

Der Server akzeptiert mode: sandbox (Standard) oder ausdrücklich mode: live. Live umgeht weder die in get_catalog veröffentlichte Verfügbarkeit noch das Mandat des Inhabers oder die Abrechnungsprüfung. USDC-Zahlungen sind derzeit geschlossen.

Senden Sie den Agentenschlüssel über Authorization: Bearer und das Mandat über mandate_id oder X-AlpNAI-Mandate. Sobald ein Angebot verfügbar ist, enthält das MCP-Ergebnis http_status:402, die x402-Anforderungen und eine REST-Fortsetzung. Das ist eine Zahlungsanforderung, kein bezahlter Beleg.

Ein HTTP-x402-Client nutzt die Fortsetzungs-URL mit derselben Idempotency-Key. Nachdem die Wallet-Richtlinie des Käufers Preis und Mandat autorisiert hat, wird PAYMENT-SIGNATURE als Anfrage-Header gesendet. Niemals einen privaten Schlüssel senden. Bei Status 202 die ursprüngliche Bestellung abfragen, ohne eine zweite Zahlung auszulösen.

Ein x402-MCP-Client kann dasselbe Tool mit ausdrücklichem Live-Modus, gleichem Mandat und Idempotenzschlüssel erneut aufrufen und den signierten PaymentPayload in params._meta["x402/payment"] übergeben. Nach bestätigter Zahlung enthält result._meta["x402/payment-response"] den x402-Beleg. HTTP-Fortsetzung bleibt verfügbar; verwenden Sie pro Anfrage nur einen Signaturtransport. Zahlungen im Sandbox-Modus werden abgelehnt. Niemals private Schlüssel übertragen.

```json
{
  "name": "purchase_snapshot",
  "arguments": {
    "mode": "live",
    "mandate_id": "OWNER_AUTHORIZED_MANDATE_ID",
    "idempotency_key": "purchase_20260915_001"
  }
}
```
