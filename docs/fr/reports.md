# Rapports et exports

Un rapport lisible pour votre équipe, un JSON structuré pour vos outils.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/reports.md) · [English](../en/reports.md) · [Deutsch](../de/reports.md)

## Choisir le bon format

Le JSON conserve les indicateurs, contrôles, décisions et paramètres dans un format réutilisable. Le HTML présente les résultats pour les lire, les partager ou les imprimer.

Dans les outils gratuits du navigateur, les fichiers sont produits localement à partir des mêmes calculs. Projects permet aussi de télécharger les résultats agrégés enregistrés dans votre compte. Aucun service de rédaction par modèle de langage n’est nécessaire pour générer ces rapports.

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

Les exports locaux ne constituent ni une facture ni une preuve de paiement. Les outils gratuits du navigateur ne conservent pas d’historique cloud : téléchargez leur rapport avant de fermer la page. Pour conserver volontairement des analyses en ligne, utilisez Projects avec votre compte ChatGPT.

## Conserver des rapports dans Projects

Projects conserve les résultats agrégés, les noms de projet/version et les identifiants nécessaires au suivi. Enregistrer un rapport transmet les mesures au serveur pour calcul ; les tentatives brutes et les prompts ne sont pas enregistrés dans la base. Une analyse locale ou un appel aux API d’analyse gratuites ne crée pas automatiquement de rapport Projects.

Le titulaire connecté peut comparer jusqu’à deux rapports, télécharger leur JSON ou un dossier imprimable. Les rapports déjà créés restent téléchargeables après la fin d’un abonnement. Supprimer un rapport retire son contenu et ses libellés, sans restituer le quota ; une empreinte et les données techniques de suivi restent conservées.

---

[Quality Gate : comparer avant de changer](quality-gate.md) · [API HTTP](api.md)
