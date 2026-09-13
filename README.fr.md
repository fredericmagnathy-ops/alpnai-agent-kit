# Kit d'intégration AlpNAI pour agents

[English](README.md) · [Deutsch](README.de.md)

Connecter un agent autorisé au **sandbox AlpNAI** et examiner une collection datée avec ses sources. Ce kit autonome contient un client Python, des exemples de messages MCP et des tests locaux. Il n'héberge pas le serveur, ne règle aucune cryptomonnaie, ne crée aucun portefeuille, ne renouvelle aucun abonnement et ne contacte aucun prospect.

**État : kit pilote préparé ; publication et activation non effectuées par ce kit, sans paiement réel.** Adresse par défaut : [alpnai.frederic150452.chatgpt.site](https://alpnai.frederic150452.chatgpt.site/). L'opérateur contrôle la visibilité du site. Si un endpoint renvoie une page de connexion ChatGPT, ce client n'a pas d'accès direct à l'API : une clé d'agent ne contourne pas l'accès de la plateforme. Utiliser le déploiement accessible documenté par l'opérateur lorsqu'il existe. Le kit ne copie aucune session de navigateur.

## Démarrer

Python 3.10 ou supérieur, sans dépendance à installer. Exécuter depuis ce répertoire.

```sh
python3 examples/buy.py --catalog
python3 examples/buy.py --sample
```

Après déploiement, obtenir une clé pilote via [/start](https://alpnai.frederic150452.chatgpt.site/start) ; l'opérateur fixe le budget fictif disponible. La première commande d'achat demande sa clé sans l'afficher. Pour une exécution automatique, fournir `ALPNAI_AGENT_KEY` via le gestionnaire de secrets du processus. Ne pas placer la clé dans le code, l'historique du terminal ou un fichier publié.

```sh
python3 examples/buy.py --product snapshot --max-usdc 0.01 --state .alpnai/snapshot-001.json
```

Relancer **la même commande** pour réessayer le même achat. Le fichier d'état conserve l'identifiant entre les exécutions ; une répétition réussie doit renvoyer le même reçu avec `replayed: true`. Conserver le fichier après un dépassement de délai. Utiliser un nouveau fichier pour un autre produit, une autre date ou une autre clé seulement s'il s'agit réellement d'un nouvel achat.

```sh
python3 examples/buy.py --product changes --since 2026-06-01 --max-usdc 0.05 --state .alpnai/changes-001.json
python3 examples/buy.py --product evidence --max-usdc 0.25 --state .alpnai/evidence-001.json
```

`ALPNAI_BASE_URL` ou `--base-url` permet de choisir une origine HTTPS autorisée par l'opérateur. HTTP est limité à la boucle locale pour les tests. Le client refuse les redirections et les chemins produits inattendus. Délai par défaut : 10 secondes par opération réseau ; au plus 3 tentatives d'achat. `--timeout` accepte au plus 60 secondes et `--attempts` au plus 4 tentatives. Seuls les incidents réseau temporaires et les erreurs HTTP 429/500/502/503/504 déclenchent une nouvelle tentative, toujours avec le même identifiant.

## Contrôles et limites

Avant l'achat, le client récupère le catalogue sans clé et exige `mode: sandbox`, `live_payments_enabled: false`, `currency: USDC` et `network: eip155:8453`. Il vérifie le chemin, le prix, sa concordance avec le montant en unités à six décimales et le plafond local `--max-usdc`. Le fichier d'état conserve une empreinte de clé, les paramètres, l'identifiant et le reçu ; jamais la clé brute.

Ce plafond porte sur **un achat fictif logique**, pas sur l'ensemble des fichiers d'état. Le serveur contrôle séparément le budget total de l'agent. La lecture du catalogue n'est pas une réservation atomique du prix : l'API ne possède pas de paramètre serveur de prix maximal. Une modification entre deux appels pourrait affecter le débit fictif. Le client refuse alors le reçu incohérent, conserve l'état et s'arrête. Ce n'est pas une protection de paiement en production.

Le reçu doit contenir `mode: sandbox`, `settled: false`, `real_revenue_usdc: 0`, le bon `simulated_price_usdc`, un identifiant et un objet de données. Aucune clé privée de portefeuille ni phrase de récupération n'est demandée. Les USDC sont simulés ; aucun jeton n'est transféré.

## Contrat et périmètre documentaire

| Route | Contrat sandbox actuel |
|---|---|
| `GET /api/v1/catalog` | Métadonnées et propositions de prix gratuites |
| `GET /api/v1/sample` | Exemple de preuves daté gratuit |
| `GET /api/v1/snapshot` | 0,01 USDC fictif |
| `GET /api/v1/changes?since=YYYY-MM-DD` | 0,05 USDC fictif ; événements de la collection après la date |
| `GET /api/v1/evidence` | 0,25 USDC fictif ; preuves et méthode |
| `POST /mcp` | Streamable HTTP ; [notes MCP en anglais](mcp/README.md) |

En-têtes d'achat : `Authorization: Bearer <test-key>`, `X-AlpNAI-Mode: sandbox`, `Idempotency-Key: <persisted-id>`. L'identifiant contient 8 à 100 lettres, chiffres, tirets ou traits de soulignement. Le [catalogue exemple](examples/catalog.sample.json) et la [copie OpenAPI](openapi.snapshot.json) sont des copies du contrat préparé, sans confirmation de l'accès public du serveur. La [provenance](contract-provenance.json) indique leur origine.

La collection initiale est datée du 14 septembre 2026 et porte sur l'annonce du dépôt confidentiel d'un projet S-1 par OpenAI le 8 juin 2026. Sa couverture est limitée et préparée à partir de sources sélectionnées. Change Set filtre les événements datés ; il ne compare pas librement toutes les versions historiques. Des champs IPO nuls ne prouvent pas l'absence d'annonces ultérieures. Les données livrées contiennent les références sources. AlpNAI est indépendant d'OpenAI et ne vend ni actions, ni allocations, ni recommandations d'investissement.

## Surveillance cloud préparée

Dépôt prévu : [fredericmagnathy-ops/alpnai-agent-kit](https://github.com/fredericmagnathy-ops/alpnai-agent-kit). Namespace MCP : `io.github.fredericmagnathy-ops/alpnai`. La publication reste une action distincte de l'opérateur.

Deux workflows GitHub Actions sont prêts : sources toutes les six heures à la minute 17 UTC, puis catalogue/exemple/MCP chaque jour à 07 h 43 UTC. Ils peuvent aussi être lancés manuellement après déploiement. Le premier consigne les résultats sans modifier les faits et échoue si une source demande une revue ou devient indisponible. Le second utilise `server/discover` et `tools/list` en MCP `2026-07-28`, sans appeler les outils d'achat.

Configurer l'adresse et les secrets autorisés, déployer l'API et placer les workflows sur la branche par défaut avant activation. Rapports limités aux statuts et compteurs, conservation sept jours, résumé dans GitHub. Une exécution en échec peut déclencher les notifications GitHub selon les réglages du compte. Le planning peut subir des retards et ne garantit pas une disponibilité continue. Configuration détaillée en anglais : [Cloud automation](CLOUD_AUTOMATION.md).

Le workflow quotidien consigne aussi un diagnostic de croissance agrégé dans une étape autorisée distincte. Le futur domaine principal est `https://alpnai.com` ; configurer `ALPNAI_BASE_URL` après liaison et vérification du domaine.

## Vérifier localement

```sh
python3 -m unittest discover -s tests -v
```

Les tests utilisent uniquement des simulations en mémoire ou un serveur HTTP local, avec des données fictives. Ils couvrent une réponse perdue après débit simulé, les réessais, les plafonds, le catalogue, le mode, les paramètres persistants, les redirections, les pages de connexion et les reçus invalides. Les tests cloud vérifient aussi les secrets, les rapports agrégés, les erreurs de revue et la découverte MCP sans achat. Ils ne valident ni un déploiement de production ni des faits financiers. Aucun compte externe n'est requis.

Les erreurs 401/403 demandent de vérifier l'accès, la révocation ou le budget ; 409 signale des paramètres différents pour le même identifiant. Après un arrêt brutal, un fichier `.lock` peut rester : vérifier qu'aucun client ne tourne avant de supprimer uniquement ce verrou, en conservant l'état de l'achat. Conserver les états et reçus dans `.alpnai/`, exclu de Git.

## Licence et contact

La [licence MIT](LICENSE) couvre uniquement le code Python. Les données, documents sources, marques et autres éléments en sont exclus ; consulter les [conditions du service](https://alpnai.frederic150452.chatgpt.site/legal) et les sources originales. Ce kit ne diffuse aucun message marketing et ne publie aucune inscription externe. Contact intégration : [frederic@alpnor.com](mailto:frederic@alpnor.com).
