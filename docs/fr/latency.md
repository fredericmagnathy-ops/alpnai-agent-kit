# Latency Lab : temps et reprises

Repérez les tâches lentes et quantifiez les tentatives supplémentaires sur les mêmes traces.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/latency.md) · [English](../en/latency.md) · [Deutsch](../de/latency.md)

## Ce que vous obtenez

Pour chaque version, examinez les durées enregistrées par tâche, leur P50, leur P95, le maximum et le nombre de reprises. Le rapport permet de comparer les mêmes tâches après un changement de modèle ou de workflow.

Les durées doivent être indiquées en millisecondes dans latency_ms, pour chaque tentative. duration_coverage indique la proportion de tâches dont toutes les tentatives ont une durée.

## Comment lire P50 et P95

Le calcul additionne les durées enregistrées des tentatives de chaque tâche. Il trie ces sommes, puis prend le rang arrondi au supérieur : ceil(0,50 × n) pour P50 et ceil(0,95 × n) pour P95.

Exemple : pour 20 tâches, P95 est la 19e valeur triée. Il décrit cet échantillon et non une garantie pour les prochaines requêtes.

## Mesurer les reprises

Reprises enregistrées = nombre de tentatives − nombre de tâches distinctes, calculé séparément pour chaque variante. Avec 40 tâches et 48 tentatives, vous avez 8 reprises enregistrées.

Comparez retry_attempts à votre propre budget de reprises. Cette version mesure le nombre de tentatives supplémentaires ; elle ne configure pas de plafond de reprises dans votre agent et ne fournit pas de compteur distinct des échecs de reprise.

## Fixer un plafond de temps

Dans config, maxP95LatencyMs fixe le plafond de P95 enregistré. Latency Lab l’évalue pour chaque groupe ; Quality Gate utilise le contrôle de la variante candidate pour sa décision.

Si une tentative n’a pas de durée, P50, P95 et le maximum du groupe deviennent null. within_p95_threshold vaut null si les durées sont incomplètes ou si aucun plafond n’a été demandé. Ne remplacez pas une durée manquante par zéro.

## Comprendre la mesure de temps

La somme des durées n’est pas le temps total perçu par l’utilisateur lorsque des tentatives s’exécutent en parallèle. Elle n’inclut pas non plus les attentes que vous n’avez pas enregistrées.

Le format n’impose ni horodatage ni ordre des tentatives. Il ne permet pas d’identifier avec certitude la première tentative ou de déduire qu’un échec précis était une reprise.

---

[Spend Proof : coût par succès](spend-proof.md) · [Quality Gate : comparer avant de changer](quality-gate.md)
