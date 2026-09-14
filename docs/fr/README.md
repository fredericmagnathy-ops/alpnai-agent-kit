# Documentation ALPNAI

Des traces à une décision vérifiable.

[Documentation sur le site](https://alpnai.com/fr/docs) · [Kit d’intégration](../../README.fr.md)

[Français](../fr/README.md) · [English](../en/README.md) · [Deutsch](../de/README.md)

Documentation du calcul gratuit et du pilote : aucune inscription à un annuaire, vente réelle ou conversion bancaire réussie n’est affirmée.

## Outils gratuits

[Spend Proof](https://alpnai.com/fr/tools/spend-proof) · [Latency Lab](https://alpnai.com/fr/tools/latency-lab) · [Quality Gate](https://alpnai.com/fr/tools/quality-gate)

Les trois outils acceptent les mêmes traces. Le calcul et les exports HTML/JSON du navigateur sont locaux ; les appels API/MCP transmettent les traces au serveur avec une clé active. Le kit Python existant reste centré sur Spend Proof.

## Démarrer

| Page | Utilité |
|---|---|
| [Comprendre ALPNAI](introduction.md) | Comparez vos agents sur le coût, les temps enregistrés et la réussite des mêmes tâches. |
| [Votre premier audit](quickstart.md) | Générez un exemple complet, lancez le calcul et récupérez un résultat expliqué. |

## Outils

| Page | Utilité |
|---|---|
| [Spend Proof : coût par succès](spend-proof.md) | Incluez les échecs et les reprises pour comparer le vrai coût des résultats enregistrés. |
| [Latency Lab : temps et reprises](latency.md) | Repérez les tâches lentes et quantifiez les tentatives supplémentaires sur les mêmes traces. |
| [Quality Gate : comparer avant de changer](quality-gate.md) | Examinez la réussite, le coût et la latence avant d’adopter une variante. |
| [Rapports et exports](reports.md) | Un rapport lisible pour votre équipe, un JSON structuré pour vos outils. |

## Intégrations

| Page | Utilité |
|---|---|
| [API HTTP](api.md) | Envoyez vos traces depuis un script et récupérez le même calcul structuré. |
| [Connecter un agent avec MCP](mcp.md) | Découvrez les outils et appelez audit_agent_costs sur vos traces. |

## Confiance

| Page | Utilité |
|---|---|
| [Paiements et mode de test](payments.md) | Distinguez les audits gratuits, les achats fictifs et le règlement x402 en cours de validation. |
| [Données et accès](security.md) | Préparez des traces minimales et choisissez où le calcul doit être effectué. |

## API gratuites

| POST | Outil |
|---|---|
| `/api/v1/spend-proof` | Spend Proof |
| `/api/v1/latency` | Latency Lab |
| `/api/v1/quality-gate` | Quality Gate |

[Huit outils MCP](mcp.md)

Les exemples MCP d’achat restent en sandbox. PayAI/x402 est en validation ; ce dépôt ne prouve aucun règlement mainnet. Aucun abonnement, commission ou virement automatique n’est exécuté par ce kit.
