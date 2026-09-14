# Connecter un agent avec MCP

Découvrez les outils et appelez audit_agent_costs sur vos traces.

[Bibliothèque de documentation](README.md) · [Documentation sur le site](https://alpnai.com/fr/docs)

[Français](../fr/mcp.md) · [English](../en/mcp.md) · [Deutsch](../de/mcp.md)

## Adresse et protocole

Utilisez POST https://alpnai.com/api/mcp. Le serveur installé expose le protocole MCP 2026-07-28 avec réponse JSON. Il utilise server/discover pour la découverte ; les exemples initialize d’anciennes versions ne décrivent pas ce contrat.

Chaque appel transmet la version du protocole, les informations du client et ses capacités dans params._meta. Les champs techniques ne sont pas traduits.

## Les outils enregistrés

get_catalog et get_free_sample servent à découvrir le pilote. audit_agent_costs, analyze_agent_latency et check_agent_quality exécutent respectivement Spend Proof, Latency Lab et Quality Gate gratuitement avec une clé active. Les trois acceptent runs et config.

purchase_snapshot, purchase_changes et purchase_evidence simulent des achats Evidence et consomment un budget fictif. Ils attendent idempotency_key ; purchase_changes peut aussi recevoir since au format YYYY-MM-DD. Le serveur expose ainsi huit outils.

## Découvrir puis appeler l’audit

Ce script Python utilise seulement la bibliothèque standard. Préparez audit.json et la variable ALPNAI_AGENT_KEY comme sur la page API. Il découvre le serveur, liste les outils puis appelle l’audit gratuit.

Les en-têtes Mcp-Method et Mcp-Name correspondent à la méthode et au nom de l’outil. structuredContent contient le rapport sans l’enveloppe data de l’API HTTP.

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

## Traiter un résultat dans votre agent

Vérifiez les erreurs JSON-RPC et result.isError avant de lire le rapport. Une réponse HTTP reçue ne suffit pas à prouver que l’outil a réussi. Lisez ensuite decision et gates pour chaque workflow.

Gardez l’exécution d’actions séparée de la lecture du rapport. Une clé ALPNAI et une recommandation d’essai ne donnent pas à l’agent un mandat de dépenses ou de déploiement.

---

[Précédent: API HTTP](api.md) · [Suivant: Paiements et mode de test](payments.md)
