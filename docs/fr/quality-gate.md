# Quality Gate : comparer avant de changer

Examinez la réussite, le coût et la latence avant d’adopter une variante.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/quality-gate.md) · [English](../en/quality-gate.md) · [Deutsch](../de/quality-gate.md)

## Définir vos seuils

Par défaut, chaque version doit avoir au moins 30 tâches distinctes. La candidate doit réussir au moins 95 % de ses tâches et perdre au maximum 2 points de pourcentage face à la référence.

Ajoutez cet objet sous config dans votre fichier de traces. maxP95LatencyMs et monthlyTasks sont facultatifs ; les autres valeurs montrées sont les valeurs par défaut.

```json
{
  "minSamples": 30,
  "minSuccessRate": 0.95,
  "maxSuccessRateDrop": 0.02,
  "maxP95LatencyMs": 3000,
  "monthlyTasks": 10000
}
```

## Lire les contrôles

both_variants : les deux versions existent. minimum_distinct_tasks_per_variant : l’échantillon atteint le minimum. same_task_set : les identifiants correspondent exactement.

observed_success_rate vérifie les seuils de réussite ; recorded_latency vérifie le plafond demandé ; lower_cost_per_successful_task exige un coût par succès strictement inférieur. pass signifie satisfait, fail non satisfait, unknown non déterminable et not_requested non demandé.

## Que faire selon la décision

missing_comparison : ajoutez la version absente. collect_more_data : complétez le nombre ou l’appariement des tâches. quality_regression : examinez les échecs selon vos critères.

latency_data_required : complétez les durées. latency_regression : le plafond est dépassé. no_economic_advantage : le coût par succès n’est pas inférieur. candidate_for_controlled_trial : préparez un essai limité.

## Préparer un essai contrôlé

Conservez les données, la configuration et le rapport. Notez ce qui a changé entre les versions, les critères de réussite et les coûts absents. Décidez ensuite d’une population et d’une durée d’essai limitées.

Le rapport contient automatic_deployment_authorized:false. Un contrôle positif ne déclenche ni changement de modèle, ni achat, ni mise en production.

## Ce que les seuils ne prouvent pas

Ces contrôles utilisent les taux observés. Les intervalles de Wilson à 95 % sont descriptifs et supposent des tâches indépendantes. Ils ne démontrent pas un effet causal ni une amélioration statistiquement établie.

experimental_bias_control reste unknown : partager des identifiants ne prouve pas un essai randomisé. Vos critères de réussite et la représentativité des tâches doivent être évalués séparément.

---

[Latency Lab : temps et reprises](latency.md) · [Rapports et exports](reports.md)
