# Connect an agent with MCP

Discover tools and call audit_agent_costs with your records.

[Documentation library](README.md) · [Website documentation](https://alpnai.com/en/docs)

[Français](../fr/mcp.md) · [English](../en/mcp.md) · [Deutsch](../de/mcp.md)

## Endpoint and protocol

Use POST https://alpnai.com/api/mcp. The server exposes MCP 2026-07-28 with server/discover and JSON responses. It also accepts MCP 2025-11-25, 2025-06-18 and 2025-03-26 clients through initialize.

Each request includes protocol version, client information and capabilities in params._meta. Technical field names are not translated.

## Earlier MCP clients

2025 clients use initialize, notifications/initialized, then tools/list and tools/call. Configure Streamable HTTP, accept application/json and text/event-stream, and send your key in Authorization: Bearer. The transport is stateless; the same key and budget checks apply. The example below uses the 2026 protocol.

## Registered tools

get_catalog and get_free_sample discover the pilot. audit_agent_costs, analyze_agent_latency and check_agent_quality run Spend Proof, Latency Lab and Quality Gate respectively, free with an active key. All three accept runs and config.

purchase_snapshot, purchase_changes and purchase_evidence simulate Evidence purchases and use a fictitious budget. They require idempotency_key; purchase_changes also accepts since as YYYY-MM-DD. The server therefore exposes eight tools.

## Discover, then call the audit

This Python script uses the standard library only. Prepare audit.json and ALPNAI_AGENT_KEY as on the API page. It discovers the server, lists tools and calls the free audit.

Mcp-Method and Mcp-Name headers match the method and tool name. structuredContent contains the report without the HTTP API’s data envelope.

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

## Handle a result in your agent

Check JSON-RPC errors and result.isError before reading the report. Receiving an HTTP response does not prove tool success. Then inspect decision and gates for each workflow.

Keep action execution separate from report reading. An ALPNAI key and trial recommendation do not grant an agent spending or deployment authority.

---

[Previous: HTTP API](api.md) · [Next: Payments and test mode](payments.md)
