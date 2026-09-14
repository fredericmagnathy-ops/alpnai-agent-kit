# Rapports et exports

Un rapport lisible pour votre équipe, un JSON structuré pour vos outils.

[Bibliothèque de documentation](README.md) · [Documentation sur le site](https://alpnai.com/fr/docs)

[Français](../fr/reports.md) · [English](../en/reports.md) · [Deutsch](../de/reports.md)

## Choisir le bon format

Le JSON conserve les indicateurs, contrôles, décisions et paramètres dans un format réutilisable. Le HTML présente les résultats pour les lire, les partager ou les imprimer.

Les fichiers sont produits localement à partir des mêmes calculs. Aucun service de rédaction par modèle de langage n’est nécessaire pour générer le rapport.

## Télécharger votre analyse

Lancez d’abord une analyse valide. Utilisez ensuite le téléchargement JSON ou HTML proposé par le module. Le navigateur enregistre le fichier sur votre appareil.

Pour un PDF, ouvrez le HTML et choisissez Imprimer, puis Enregistrer en PDF si votre navigateur le permet. Ce PDF provient de votre navigateur, pas d’un service de conversion externe.

## Lire un rapport provenant de l’API

L’API Spend Proof renvoie une enveloppe contenant mode, payment_required, persisted et data. Le rapport se trouve dans data. Le script ci-dessous lit la réponse enregistrée par l’exemple de la page API.

Il extrait le rapport dans audit-report.json. Il n’ajoute pas de commentaire généré et n’envoie aucune information ailleurs.

```python
import json
from pathlib import Path

response = json.loads(Path("audit-response.json").read_text(encoding="utf-8"))
if response.get("error"):
    raise SystemExit(response["error"])
report = response["data"]
for item in report["workflows"]:
    print(item["workflow"], item["decision"])
    print(item["baseline"]["cost_per_successful_task_usd"])
    print(item["candidate"]["cost_per_successful_task_usd"])
Path("audit-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
```

## Conserver un résultat interprétable

Conservez la provenance du jeu de données et les seuils du test. Un exemple fictif doit rester identifié comme tel, même après export. Gardez vos rapports à l’abri si les identifiants révèlent votre activité.

Les exports locaux ne constituent ni une facture ni une preuve de paiement. La page ne fournit pas d’historique cloud des audits : sauvegardez le rapport avant de fermer votre session.

---

[Précédent: Quality Gate : comparer avant de changer](quality-gate.md) · [Suivant: API HTTP](api.md)
