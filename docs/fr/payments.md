# Paiements et mode de test

Distinguez les audits gratuits, les achats fictifs et le règlement x402 en cours de validation.

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

Avant toute demande 402, le parcours préparé exige un profil et une revue de facturation valables, liés aux conditions acceptées. Le devis fige alors le total et les coordonnées utilisées. Saisir un profil ne constitue pas une vérification fiscale ; aucun processus de délivrance de revue n’est encore ouvert.

Le serveur prépare une commande et indique ses conditions de paiement avec une réponse 402. Un agent acheteur autorisé peut alors produire l’autorisation correspondante. Le service vérifie le montant, le réseau, le destinataire et le mandat avant de traiter le règlement.

Le facilitateur aide à vérifier et régler le paiement. Un état pending ou unknown demande une vérification de la commande originale ; il ne doit pas déclencher une nouvelle dépense automatique.

## Retrouver une commande et son reçu

Une commande en attente conserve le même identifiant. Le rapprochement cherche la preuve du paiement dans les blocs finalisés, par pages limitées avec une position de reprise conservée. Une panne ou un retard ne déclenche jamais une nouvelle tentative de règlement.

Une réservation abandonnée avant toute tentative est libérée à expiration du devis. Dès qu’une tentative a commencé, elle reste en vérification : le budget n’est pas libéré sur la seule base d’un délai.

Après confirmation, le titulaire retrouve le reçu et le résultat dans son espace client. Les compteurs de recettes incluent uniquement les règlements confirmés en USDC sur Base ; les essais et les paiements sur réseau de test restent exclus.

## Imprimer un reçu confirmé

Dans l’espace client, une commande confirmée propose « Reçu et résultat » pour le fichier JSON et « Reçu imprimable » pour une page lisible. Ouvrez cette page, puis utilisez Imprimer dans le navigateur pour imprimer ou enregistrer un PDF.

Le reçu conserve les coordonnées et montants du devis associé, même après modification du profil. Il indique la confirmation enregistrée en UTC, la transaction et les empreintes des documents. Une ancienne commande sans coordonnées figées reste un reçu minimal. Le document ne remplace pas une facture fiscale.

Seul le compte titulaire peut ouvrir ce document privé. Aucun reçu imprimable n’est produit pour une commande non confirmée ; la consultation ne contacte pas le facilitateur et ne déclenche aucun paiement. Les achats réels restent désactivés.

```http
GET /api/account/orders/{order_id}/receipt?lang=fr
```

## Du portefeuille à la banque

Le paiement prévu est en USDC sur Base vers le portefeuille du vendeur, accessible avec MetaMask. Convertir ensuite ces recettes en CHF ou EUR et les envoyer à la banque relève d’un prestataire distinct.

Ce parcours ne repose pas sur Coinbase Business. Le prestataire de conversion doit accepter l’activité du vendeur et son compte bancaire ; ses cours, frais et délais s’appliquent. Le client achète un service, pas un placement, un rendement ou une allocation IPO.

[ALPNAI documentation](https://alpnai.com/fr/docs/payments)
