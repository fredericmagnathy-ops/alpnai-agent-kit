# Einen Agenten über MCP verbinden

Entdecken Sie Werkzeuge und rufen Sie audit_agent_costs mit Ihren Aufzeichnungen auf.

[Dokumentationsbibliothek](README.md) · [Dokumentation auf der Website](https://alpnai.com/de/docs)

[Français](../fr/mcp.md) · [English](../en/mcp.md) · [Deutsch](../de/mcp.md)

## Endpunkt und Protokoll

Verwenden Sie POST https://alpnai.com/api/mcp. Der installierte Server stellt MCP 2026-07-28 mit JSON-Antworten bereit. Die Erkennung nutzt server/discover; initialize-Beispiele älterer Versionen beschreiben diesen Vertrag nicht.

Jede Anfrage enthält Protokollversion, Clientinformationen und Fähigkeiten unter params._meta. Technische Feldnamen werden nicht übersetzt.

## Registrierte Werkzeuge

get_catalog und get_free_sample dienen zur Erkundung des Piloten. audit_agent_costs, analyze_agent_latency und check_agent_quality führen Spend Proof, Latency Lab beziehungsweise Quality Gate mit aktivem Schlüssel kostenlos aus. Alle drei akzeptieren runs und config.

purchase_snapshot, purchase_changes und purchase_evidence simulieren Evidence-Käufe mit fiktivem Budget. Sie benötigen idempotency_key; purchase_changes akzeptiert zusätzlich since im Format YYYY-MM-DD. Der Server stellt damit acht Werkzeuge bereit.

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

---

[Zurück: HTTP-API](api.md) · [Weiter: Zahlungen und Testmodus](payments.md)
