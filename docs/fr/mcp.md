# Connecter un agent avec MCP

Découvrez les outils et appelez audit_agent_costs sur vos traces.

## Adresse et protocole

Utilisez POST https://alpnai.com/api/mcp. Le serveur expose MCP 2026-07-28 avec server/discover pour la découverte et des réponses JSON. Il accepte aussi les clients MCP 2025-11-25, 2025-06-18 et 2025-03-26 via initialize.

Chaque appel transmet la version du protocole, les informations du client et ses capacités dans params._meta. Les champs techniques ne sont pas traduits.

## Clients MCP antérieurs

Les clients 2025 utilisent initialize, notifications/initialized, puis tools/list et tools/call. Configurez le transport Streamable HTTP, acceptez application/json et text/event-stream, et envoyez votre clé dans Authorization: Bearer. Le mode est sans session persistante ; les mêmes contrôles de clé et de budget s’appliquent. L’exemple ci-dessous utilise le protocole 2026.

## Les outils enregistrés

get_catalog et get_free_sample servent à découvrir le pilote. audit_agent_costs, analyze_agent_latency et check_agent_quality exécutent respectivement Spend Proof, Latency Lab et Quality Gate gratuitement avec une clé active. Les trois acceptent runs et config.

purchase_snapshot, purchase_changes et purchase_evidence utilisent par défaut le mode sandbox et consomment un budget de test. Ils attendent idempotency_key ; purchase_changes peut aussi recevoir since au format YYYY-MM-DD. Le serveur expose ainsi dix outils.

save_project_report calcule et enregistre un rapport dans le projet autorisé explicitement par son titulaire, avec le quota Projects existant. Il attend request_id, title et input. Guide : https://alpnai.com/fr/docs/projects-automation.

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

## Tester depuis un agent, sans compte

GET /api/v1/performance-sample renvoie les mesures d’un exemple synthétique et les résultats réellement calculés : coût, latence et qualité. Aucun compte, portefeuille ou paiement n’est nécessaire pour cet exemple.

Le catalogue REST et l’outil MCP get_catalog décrivent les mêmes analyses, leurs entrées, sorties, prix et accès. Pour analyser vos propres mesures, activez une clé une fois ; votre agent peut ensuite appeler les outils sans intervention du propriétaire d’ALPNAI.

Le programme verify-performance-sample.mjs du kit récupère le catalogue et l’exemple, recalcule les mesures et renvoie PASS ou FAIL. Il ne lance aucun achat. La réussite de ce contrôle valide l’exemple et son calcul, pas un encaissement crypto.

```
GET https://alpnai.com/api/v1/catalog
GET https://alpnai.com/api/v1/performance-sample
```

## Demander un achat depuis MCP

Le serveur accepte mode: sandbox (par défaut) ou mode: live demandé explicitement. Le mode live ne contourne ni la disponibilité commerciale publiée dans get_catalog, ni le mandat du propriétaire, ni la qualification de facturation. Les encaissements USDC restent actuellement fermés.

Transmettez la clé dans Authorization: Bearer et le mandat dans mandate_id ou X-AlpNAI-Mandate. Si un devis devient disponible, le résultat MCP contient http_status:402, les exigences x402 et une continuation REST. Ce résultat est une demande de paiement, pas un reçu payé.

Un client x402 HTTP utilise l’URL de continuation et la même Idempotency-Key. Après validation du prix et du mandat par la politique du portefeuille acheteur, PAYMENT-SIGNATURE doit être transmis comme en-tête. N’envoyez jamais de clé privée. Un état 202 se suit avec l’URL de commande originale, sans second paiement.

Un client MCP x402 peut répéter le même outil, avec mode live, le même mandat et la même clé d’idempotence, en plaçant le PaymentPayload signé dans params._meta["x402/payment"]. Après confirmation du règlement, result._meta["x402/payment-response"] contient le reçu x402. La continuation HTTP reste disponible ; utilisez un seul transport de signature par requête. Un paiement joint au mode sandbox est refusé. Aucune clé privée ne doit être transmise.

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

## Suivre la commande sans nouveau paiement

Après un achat renvoyant http_status:202, appelez get_order avec l’order_id original et votre clé d’agent. Respectez Retry-After puis répétez uniquement ce suivi. Le résultat pending est une consultation réussie, pas encore une livraison payée.

Ce dixième outil peut enregistrer la preuve finalisée du paiement ou annuler une réservation expirée avant toute soumission, avec libération unique du budget. Il ne crée aucun achat et refuse les signatures jointes. Il fonctionne aussi lorsque les nouveaux achats sont désactivés.

Le reçu confirmé et le livrable original reviennent dans structuredContent ; le reçu x402 est aussi disponible dans result._meta["x402/payment-response"]. Un état cancelled_before_submission signifie qu’aucune soumission n’a été engagée par ALPNAI pour cette commande.

```json
{
  "name": "get_order",
  "arguments": {
    "order_id": "ORIGINAL_ORDER_ID"
  }
}
```
