# Votre premier audit

Générez un exemple complet, lancez le calcul et récupérez un résultat expliqué.

[Bibliothèque de documentation](README.md) · [Documentation sur le site](https://alpnai.com/fr/docs)

[Français](../fr/quickstart.md) · [English](../en/quickstart.md) · [Deutsch](../de/quickstart.md)

## 1. Créer un fichier de démonstration

Le script Python ci-dessous crée audit.json avec 40 tâches par version, soit 80 tentatives. Toutes les données sont fictives. Les deux versions réussissent les mêmes 39 tâches.

Vous pouvez aussi charger la démonstration proposée dans l’outil, sans installer Python.

```python
import json
from pathlib import Path

runs = []
for number in range(1, 41):
    task_id = f"demo-{number:03d}"
    for variant, cost, latency in [
        ("baseline", 0.04, 2200),
        ("candidate", 0.025, 1600),
    ]:
        runs.append({
            "task_id": task_id,
            "workflow": "invoice_fields",
            "variant": variant,
            "cost_usd": cost,
            "success": number != 40,
            "latency_ms": latency,
        })

audit = {"runs": runs, "config": {"maxP95LatencyMs": 3000}}
Path("audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
```

## 2. Analyser les traces

Ouvrez Spend Proof, chargez audit.json ou collez son contenu, puis lancez l’analyse. Commencez avec les seuils par défaut ; l’exemple fixe seulement un plafond P95 de 3 000 ms.

Pour vos données, conservez un identifiant opaque par tâche, répété pour baseline et candidate. Chaque nouvelle tentative occupe une ligne distincte.

## 3. Lire le résultat

La référence coûte 1,60 USD au total ; la variante coûte 1,00 USD. Chacune obtient 39 réussites sur 40 tâches. Le P95 enregistré est respectivement de 2 200 ms et 1 600 ms.

Avec ces données fictives, la décision attendue est candidate_for_controlled_trial. Cela signifie « candidat pour un essai contrôlé », pas « déployer automatiquement ».

## 4. Enregistrer et refaire avec vos données

Téléchargez le JSON pour une autre application et le HTML pour lire ou imprimer le rapport. Gardez l’exemple clairement marqué comme fictif.

Refaites ensuite le même parcours avec des coûts complets et des critères de réussite définis avant le test. La page API explique comment automatiser ce calcul gratuit.

---

[Précédent: Comprendre ALPNAI](introduction.md) · [Suivant: Spend Proof : coût par succès](spend-proof.md)
