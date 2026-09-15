# Comprendre ALPNAI

Comparez vos agents sur le coût, les temps enregistrés et la réussite des mêmes tâches.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/introduction.md) · [English](../en/introduction.md) · [Deutsch](../de/introduction.md)

## La question à résoudre

Votre agent peut devenir moins cher par appel mais plus coûteux par résultat s’il recommence ou échoue. ALPNAI part des tentatives réellement enregistrées et les regroupe par tâche.

Vous comparez une référence, baseline, à une variante, candidate. Le résultat aide à choisir ce qu’il faut tester ensuite.

## Choisir votre outil

Spend Proof : comparez le coût par tâche réussie. Latency Lab : examinez P50, P95 et les reprises enregistrées. Quality Gate : vérifiez les seuils avant un essai limité.

Les trois lectures utilisent le même format de traces. Vous pouvez télécharger un rapport JSON pour un agent et un rapport HTML lisible pour votre équipe.

## Un parcours simple

Préparez les mêmes identifiants de tâches pour les deux versions. Importez les coûts complets, vos étiquettes de réussite et, si disponibles, les durées. Analysez, lisez les contrôles, puis enregistrez le rapport.

Le calcul dans le navigateur ne demande pas de compte. L’API et MCP demandent une clé ALPNAI active ; l’audit reste gratuit.

Projects ajoute un historique privé et la comparaison de rapports enregistrés. Connectez-vous avec ChatGPT pour utiliser les trois rapports gratuits ou choisir un abonnement Stripe. Cet espace est distinct des API/MCP gratuites et des achats crypto en test.

## Ce que la mesure signifie

Les résultats décrivent les données fournies. ALPNAI ne remplace pas votre définition d’un bon résultat et ne modifie pas vos agents. Un candidat intéressant doit encore être éprouvé dans votre environnement.

Les services Evidence sur l’IPO OpenAI constituent un pilote distinct. Leurs achats de test et budgets fictifs ne sont pas des ventes ou des placements.

## Tester depuis un agent, sans compte

GET /api/v1/performance-sample renvoie les mesures d’un exemple synthétique et les résultats réellement calculés : coût, latence et qualité. Aucun compte, portefeuille ou paiement n’est nécessaire pour cet exemple.

Le catalogue REST et l’outil MCP get_catalog décrivent les mêmes analyses, leurs entrées, sorties, prix et accès. Pour analyser vos propres mesures, activez une clé une fois ; votre agent peut ensuite appeler les outils sans intervention du propriétaire d’ALPNAI.

Le programme verify-performance-sample.mjs du kit récupère le catalogue et l’exemple, recalcule les mesures et renvoie PASS ou FAIL. Il ne lance aucun achat. La réussite de ce contrôle valide l’exemple et son calcul, pas un encaissement crypto.

```
GET https://alpnai.com/api/v1/catalog
GET https://alpnai.com/api/v1/performance-sample
```

---

[Votre premier audit](quickstart.md)
