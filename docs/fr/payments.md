# Paiements et mode de test

Distinguez les audits gratuits, les achats fictifs et le règlement x402 en cours de validation.

[Bibliothèque de documentation](README.md) · [Documentation sur le site](https://alpnai.com/fr/docs)

[Français](../fr/payments.md) · [English](../en/payments.md) · [Deutsch](../de/payments.md)

## Ce qui peut être utilisé aujourd’hui

Spend Proof et les calculs locaux ne demandent aucun paiement. Le pilote Evidence permet d’essayer des achats avec une clé et un budget fictif.

Une intégration x402 utilisant PayAI est préparée pour USDC sur Base, mais le parcours de paiement principal reste en validation. Sa présence dans le code ne signifie pas qu’une vente réelle ou un règlement complet a été effectué.

## Essayer sans transfert de fonds

Cette requête appelle une route existante en mode sandbox. Son reçu indique settled:false, real_revenue_usdc:0 et un prix simulé. Elle ne nécessite pas la connexion d’un portefeuille.

Renvoyez la même requête avec la même Idempotency-Key pour retrouver le même achat. Réutiliser cet identifiant avec d’autres paramètres produit un conflit ; choisissez un nouvel identifiant pour une nouvelle commande.

```bash
curl --fail-with-body --silent --show-error \
  'https://alpnai.com/api/v1/snapshot' \
  --header "Authorization: Bearer ${ALPNAI_AGENT_KEY}" \
  --header 'X-ALPNAI-Mode: sandbox' \
  --header 'Idempotency-Key: docs_demo_20260914_001'
```

## Comprendre le futur échange x402

Le serveur prépare une commande et indique ses conditions de paiement avec une réponse 402. Un agent acheteur autorisé peut alors produire l’autorisation correspondante. Le service vérifie le montant, le réseau, le destinataire et le mandat avant de traiter le règlement.

Le facilitateur aide à vérifier et régler le paiement. Un état pending ou unknown demande une vérification de la commande originale ; il ne doit pas déclencher une nouvelle dépense automatique.

## Du portefeuille à la banque

Le paiement prévu est en USDC sur Base vers le portefeuille du vendeur, accessible avec MetaMask. Convertir ensuite ces recettes en CHF ou EUR et les envoyer à la banque relève d’un prestataire distinct.

Ce parcours ne repose pas sur Coinbase Business. Le prestataire de conversion doit accepter l’activité du vendeur et son compte bancaire ; ses cours, frais et délais s’appliquent. Le client achète un service, pas un placement, un rendement ou une allocation IPO.

---

[Précédent: Connecter un agent avec MCP](mcp.md) · [Suivant: Données et accès](security.md)
