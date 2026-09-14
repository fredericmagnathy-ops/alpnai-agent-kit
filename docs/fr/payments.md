# Projects, paiements et mode de test

Distinguez les abonnements Projects par carte, les analyses gratuites et les achats USDC encore en test.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/payments.md) · [English](../en/payments.md) · [Deutsch](../de/payments.md)

## Ce qui peut être utilisé aujourd’hui

Spend Proof, Latency Lab et Quality Gate proposent des calculs gratuits. Projects est un espace privé accessible avec ChatGPT : trois rapports enregistrés gratuits à vie et des abonnements Stripe ouverts sur le site. Le pilote Evidence permet d’essayer des achats API/MCP avec une clé et un budget fictif.

Les achats réels USDC sur Base restent désactivés. L’intégration x402 utilisant PayAI est préparée ; sa présence dans le code ne signifie pas qu’une vente réelle ou un règlement complet a eu lieu. L’ouverture des abonnements Projects ne change pas le mode de test des achats crypto.

## Souscrire à Projects et gérer les factures

Selon les devises proposées dans Projects, le titulaire connecté choisit 19 CHF, 19 EUR, 19 USD ou 19 GBP par mois pour 100 nouveaux rapports par période mensuelle payée, ou 190 CHF, 190 EUR, 190 USD ou 190 GBP par an pour 1 200 par période annuelle payée. Les offres comprennent 10 projets. Il s’agit de tarifs locaux distincts, taxes incluses dans le total présenté par Stripe ; aucune conversion de devises n’est annoncée.

Le titulaire accepte les conditions Projects avant Stripe Checkout. L’abonnement se renouvelle à la fréquence choisie jusqu’à résiliation ; le portail Abonnement et factures permet d’arrêter le prochain renouvellement et de gérer les factures. L’accès gratuit ne devient pas automatiquement payant. Un paiement échoué n’accorde pas une nouvelle période.

Le serveur vérifie un paiement conforme avant d’ouvrir une période payée. Un retour de Stripe, une session de paiement créée ou un test de notification ne constitue pas une vente. Les outils MCP et clients Python du kit ne souscrivent pas cet abonnement ; une clé agent ne donne aucun accès au portail privé.

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

Avant toute demande 402, le parcours préparé exige un profil et une revue de facturation valables, liés aux conditions acceptées. Le devis fige alors le total et les coordonnées utilisées. La console privée permet à l’opérateur de consigner une décision justifiée, sa validité et sa révocation. Le client et son agent ne peuvent pas approuver leur propre dossier. Une saisie correcte ne vérifie pas à elle seule la situation fiscale ; les paiements réels USDC restent désactivés.

Le serveur prépare une commande et indique ses conditions de paiement avec une réponse 402. Un agent acheteur autorisé peut alors produire l’autorisation correspondante. Le service vérifie le montant, le réseau, le destinataire et le mandat avant de traiter le règlement.

Le facilitateur aide à vérifier et régler le paiement. Un état pending ou unknown demande une vérification de la commande originale ; il ne doit pas déclencher une nouvelle dépense automatique.

## Retrouver une commande et son reçu

Une commande en attente conserve le même identifiant. Le rapprochement cherche la preuve du paiement dans les blocs finalisés, par pages limitées avec une position de reprise conservée. Une panne ou un retard ne déclenche jamais une nouvelle tentative de règlement.

Une réservation abandonnée avant toute tentative est libérée à expiration du devis. Dès qu’une tentative a commencé, elle reste en vérification : le budget n’est pas libéré sur la seule base d’un délai.

Après confirmation, le titulaire retrouve le reçu et le résultat dans son espace client. Les compteurs de recettes incluent uniquement les règlements confirmés en USDC sur Base ; les essais et les paiements sur réseau de test restent exclus.

## Imprimer un reçu confirmé

Dans l’espace client, une commande confirmée propose « Reçu et résultat » pour le fichier JSON et « Reçu imprimable » pour une page lisible. Ouvrez cette page, puis utilisez Imprimer dans le navigateur pour imprimer ou enregistrer un PDF.

Le reçu conserve les coordonnées et montants du devis associé, même après modification du profil. Il indique la confirmation enregistrée en UTC, la transaction et les empreintes des documents. Une ancienne commande sans coordonnées figées reste un reçu minimal. Le document ne remplace pas une facture fiscale.

Seul le compte titulaire peut ouvrir ce document privé. Aucun reçu imprimable n’est produit pour une commande non confirmée ; la consultation ne contacte pas le facilitateur et ne déclenche aucun paiement. Les achats réels USDC restent désactivés.

```http
GET /api/account/orders/{order_id}/receipt?lang=fr
```

## Du portefeuille à la banque

Le paiement prévu est en USDC sur Base vers le portefeuille du vendeur, accessible avec MetaMask. Convertir ensuite ces recettes en CHF ou EUR et les envoyer à la banque relève d’un prestataire distinct.

Ce parcours ne repose pas sur Coinbase Business. Le prestataire de conversion doit accepter l’activité du vendeur et son compte bancaire ; ses cours, frais et délais s’appliquent. Le client achète un service, pas un placement, un rendement ou une allocation IPO.

---

[Automatiser la livraison de rapports](projects-automation.md) · [Données et accès](security.md)
