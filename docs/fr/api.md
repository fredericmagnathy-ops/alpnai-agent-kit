# API HTTP

Envoyez vos traces depuis un script et récupérez le même calcul structuré.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/api.md) · [English](../en/api.md) · [Deutsch](../de/api.md)

## Obtenir une clé

Ouvrez /start, connectez-vous et créez l’accès de test. La clé est générée par le service ; copiez-la lorsqu’elle apparaît. alp_test_… indique son format, ce n’est pas une valeur à inventer.

Conservez la clé dans une variable d’environnement ALPNAI_AGENT_KEY sur votre machine ou votre serveur. Une adresse de portefeuille ne remplace pas cette clé.

## Calculer un audit

Préparez audit.json avec la page de démarrage, puis exécutez cette requête. POST /api/v1/spend-proof attend un JSON runs/config et une clé active. Aucun en-tête de paiement n’est demandé pour cet audit gratuit.

L’exemple enregistre la réponse dans audit-response.json. Il utilise les variables de votre environnement et n’inscrit pas la clé dans le code.

```bash
curl --fail-with-body --silent --show-error \
  'https://alpnai.com/api/v1/spend-proof' \
  --header "Authorization: Bearer ${ALPNAI_AGENT_KEY}" \
  --header 'Content-Type: application/json' \
  --data-binary @audit.json \
  --output audit-response.json
```

## Contrat et taille des données

Limites : de 1 à 1 000 tentatives, au plus 512 000 octets UTF-8. Le coût d’une tentative est compris entre 0 et 10 000 USD ; une durée entre 0 et 86 400 000 ms. Les champs inconnus et valeurs d’un type incorrect sont rejetés.

Une réponse réussie contient mode:"free_audit", payment_required:false, persisted:false et data. persisted:false décrit l’absence d’enregistrement des traces dans la base applicative, pas une suppression de tous les journaux d’infrastructure.

## Traiter les erreurs

400 invalid_audit_input : corrigez le JSON, les champs ou leurs limites. 401 agent_key_required : vérifiez la clé et son activation. 403 origin_forbidden : les appels de navigateur depuis une autre origine sont refusés.

413 body_too_large : réduisez le fichier en conservant des tâches appariées complètes. 503 audit_unavailable : le service n’a pas pu traiter la demande ; prévoyez une reprise limitée. Une décision collect_more_data dans une réponse 200 est un résultat d’analyse, pas une panne HTTP.

## Autres routes disponibles

Les trois calculs gratuits acceptent le même JSON et la même clé : POST /api/v1/spend-proof, POST /api/v1/latency et POST /api/v1/quality-gate. Remplacez seulement le chemin dans l’exemple ci-dessus pour choisir le calcul.

L’API latency renvoie groups avec notamment p50_ms, p95_ms, max_ms et retry_attempts ; quality-gate renvoie workflows avec comparison, gates, decision et les taux de réussite. GET /openapi.json décrit le contrat ; GET /api/v1/catalog et GET /api/v1/sample sont publics. L’export HTML reste généré localement.

---

[Rapports et exports](reports.md) · [Connecter un agent avec MCP](mcp.md)
