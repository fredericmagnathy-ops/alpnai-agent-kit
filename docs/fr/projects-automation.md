# Automatiser la livraison de rapports

Ajoutez un rapport Projects à la fin de chaque évaluation, sans import manuel.

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/projects-automation.md) · [English](../en/projects-automation.md) · [Deutsch](../de/projects-automation.md)

## Une évaluation terminée, un rapport conservé

Une agence qui teste plusieurs agents peut perdre du temps à réunir ses résultats. Ajoutez un appel ALPNAI à la fin de votre propre pipeline : le serveur calcule les coûts, la latence et les contrôles de qualité, puis conserve le résultat dans Projects.

Votre équipe retrouve un historique privé pour comparer deux versions et télécharger un dossier. Vous fournissez les traces et vos critères de réussite ; ALPNAI ne lance pas les modèles et ne change pas leur configuration.

## Autoriser une destination une seule fois

Connectez-vous à https://alpnai.com/projects avec le compte qui détient les rapports. Activez votre clé dans https://alpnai.com/account si nécessaire. Dans « Vos rapports, livrés par votre agent », choisissez le projet, acceptez l’utilisation du quota puis cliquez sur « Autoriser les dépôts ».

Cette autorisation concerne votre agent actif et un projet fixe. Elle permet uniquement de calculer et déposer de nouveaux rapports. Elle ne permet ni de lire les anciens rapports, ni de les supprimer, ni de payer ou de souscrire un abonnement. Le bouton « Arrêter les dépôts » révoque l’accès.

## Connecter votre pipeline

Envoyez POST https://alpnai.com/api/v1/project-reports avec Authorization: Bearer et votre clé ALPNAI. Le corps contient request_id, title et input. input reprend le format runs/config des outils gratuits. Aucun user_id ou project n’est accepté : la destination vient de votre autorisation.

Avec MCP, appelez save_project_report avec les mêmes arguments. Vérifiez result.isError. Une réponse réussie fournit un identifiant de rapport, saved: true et persistence: computed_summary. Le contenu est consultable par le titulaire dans Projects.

Limitez chaque envoi à 1 000 tentatives et à 500 000 octets pour rester sous les limites des deux transports. Envoyez uniquement des mesures sans prompts, secrets ou données personnelles. Les tentatives brutes ne sont pas enregistrées dans la base ; les résultats agrégés, libellés et identifiants techniques le sont.

Exemple de format avec deux tentatives synthétiques, sans preuve d’économies. Remplacez les mesures et créez un identifiant propre à chaque nouveau rapport.

```json
{
  "request_id": "e5b67ec8-5d1a-4abe-9e1b-5f358557db82",
  "title": "Evaluation 2026-09-15",
  "input": {
    "runs": [
      {
        "task_id": "synthetic-1",
        "workflow": "support",
        "variant": "baseline",
        "cost_usd": 0.02,
        "success": true,
        "latency_ms": 200
      },
      {
        "task_id": "synthetic-1",
        "workflow": "support",
        "variant": "candidate",
        "cost_usd": 0.01,
        "success": true,
        "latency_ms": 180
      }
    ]
  }
}
```

## Reprendre sans compter deux fois

Créez et conservez un UUID avant chaque nouveau rapport. Pour reprendre après une coupure, réutilisez exactement le même request_id, titre, données et autorisation. Le serveur renvoie le même identifiant avec replayed: true et ne reprend pas de quota. Un contenu différent avec le même identifiant est refusé.

Un changement de projet ou une nouvelle autorisation crée un nouvel espace d’identifiants. Terminez les envois en cours avant ce changement. Une clé révoquée ne fonctionne plus ; son renouvellement exige de mettre à jour votre secret dans le pipeline. Ne créez pas de nouveaux identifiants pour contourner une erreur de quota.

## Un quota partagé, des coûts lisibles

Les dépôts automatiques et manuels utilisent ensemble les trois rapports gratuits à vie, ou les 100 rapports de la période mensuelle payée, ou les 1 200 rapports de la période annuelle payée. Il n’y a aucun dépassement facturé et aucun passage automatique à une offre payante.

Les abonnements sont de 19 CHF, EUR, USD ou GBP par mois, ou 190 dans la même devise par an. Le titulaire choisit et confirme son abonnement sur le site. À quota épuisé, l’API refuse un nouvel enregistrement ; vos analyses gratuites restent disponibles.

## Résoudre les erreurs

401 agent_key_required : vérifiez la clé active. 403 project_access_required ou project_access_revoked : le titulaire doit vérifier l’autorisation. 409 report_limit_reached : consultez le quota Projects. 409 report_request_conflict : reprenez les paramètres initiaux. 400 invalid_report : vérifiez le format.

Après un délai d’attente ou une indisponibilité temporaire, reprenez avec le même identifiant. Un rapport supprimé ne peut pas être recréé sous le même identifiant. Les règles complètes de conservation et de facturation figurent dans les conditions Projects.

## Client Python prêt à intégrer

Depuis le dépôt, fournissez ALPNAI_AGENT_KEY via votre gestionnaire de secrets, puis utilisez vos propres mesures. Un nouvel état correspond à un nouveau rapport. Reprenez exactement la même commande après une interruption.

```sh
python3 examples/save_project.py --input private/attempts.json --title "Extraction v2" --state private/extraction-v2-state.json
```

Le client conserve l’identifiant et une empreinte dans un fichier privé avant l’envoi ; il refuse les redirections et toute modification des paramètres d’une reprise. Ne réutilisez pas une ancienne commande après avoir changé l’autorisation de projet.

---

[Connecter un agent avec MCP](mcp.md) · [Projects, paiements et mode de test](payments.md)
