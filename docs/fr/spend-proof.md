# Spend Proof : coût par succès

Incluez les échecs et les reprises pour comparer le vrai coût des résultats enregistrés.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/spend-proof.md) · [English](../en/spend-proof.md) · [Deutsch](../de/spend-proof.md)

## Le format des données

Chaque ligne représente une tentative : task_id, workflow, variant, cost_usd et success sont obligatoires. latency_ms est facultatif. Les noms de champs restent en anglais dans toutes les langues.

Cet exemple de deux lignes montre le format ; il ne suffit pas aux 30 tâches distinctes par version requises par défaut pour comparer.

```json
{
  "runs": [
    {
      "task_id": "task-01",
      "workflow": "invoice_fields",
      "variant": "baseline",
      "cost_usd": 0.04,
      "success": true,
      "latency_ms": 2200
    },
    {
      "task_id": "task-01",
      "workflow": "invoice_fields",
      "variant": "candidate",
      "cost_usd": 0.025,
      "success": true,
      "latency_ms": 1600
    }
  ]
}
```

## Quels coûts inclure

Additionnez les coûts du modèle, des outils, de la recherche et des autres appels nécessaires à la tentative. Enregistrez aussi les tentatives échouées. Convertissez toutes les valeurs en USD avant l’import.

cost_usd accepte au plus six décimales. Pour des coûts plus fins, agrégez-les correctement en amont. Une chaîne comme "0.04" n’est pas un nombre et sera rejetée.

## Comment le coût est calculé

Les tentatives sont regroupées par workflow, variant et task_id. Une tâche est déclarée réussie si au moins une de ses tentatives porte success:true. Tous ses coûts sont comptés.

Coût par tâche réussie = coût total des tentatives ÷ nombre de tâches réussies. S’il n’y a aucune réussite, le résultat est null : aucun coût par succès fini ne peut être calculé.

## Une projection mensuelle comparable

monthlyTasks indique le volume mensuel de tâches lancées par la référence. Il ne peut être utilisé que pour un seul workflow. La projection compare ensuite un même volume attendu de résultats réussis.

Elle apparaît uniquement pour un candidat admissible à un essai contrôlé. Elle exclut notamment intégration, migration, évaluation et valeur économique des erreurs. realized_savings_usd reste null : une projection n’est pas une économie encaissée.

## Préparer une comparaison fiable

Utilisez exactement les mêmes task_id pour les deux variantes et la même définition du succès. Le même task_id ne peut pas appartenir à plusieurs workflows. Séparez vos environnements ou jeux d’essai avant l’export.

Les doublons comptent comme des tentatives supplémentaires. Dédupliquez donc votre télémétrie en amont. Le moteur ne peut détecter une facture manquante ni prouver que votre échantillon représente tous vos clients.

---

[Projects : rapports privés et abonnements](projects.md) · [Latency Lab : temps et reprises](latency.md)
