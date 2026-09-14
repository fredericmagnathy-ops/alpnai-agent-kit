# ALPNAI Projects — documentez vos décisions sur les agents

Révision : 14 septembre 2026.

Comparez le coût, le taux de réussite et la latence de deux versions avant de choisir laquelle conserver. Projects enregistre les résultats agrégés de **Spend Proof, Latency Lab et Quality Gate** dans votre compte privé, avec téléchargements JSON et dossiers imprimables. Le résultat dépend de vos mesures ; une projection ne garantit pas une économie.

[Ouvrir Projects](https://alpnai.com/projects) · [Conditions](https://alpnai.com/fr/legal/projects) · [Confidentialité](https://alpnai.com/fr/legal/privacy)

[Bibliothèque de documentation](README.md) · [ALPNAI](https://alpnai.com/fr/docs)

[Français](../fr/projects.md) · [English](../en/projects.md) · [Deutsch](../de/projects.md)

## Accès et offres

Connectez-vous avec ChatGPT. Projects est réservé au titulaire authentifié ; une clé API d’agent n’ouvre ni ses rapports ni sa facturation. Aucun portefeuille crypto n’est nécessaire.

| Offre | Prix | Nouveaux rapports enregistrés |
|---|---|---|
| Accès gratuit | Sans carte | 3 à vie par compte |
| Mensuelle | 19 CHF, 19 EUR, 19 USD ou 19 GBP par mois | 100 par période mensuelle payée |
| Annuelle | 190 CHF, 190 EUR, 190 USD ou 190 GBP par an | 1 200 par période annuelle payée |

Projects permet 10 projets et au maximum 2 400 rapports conservés. Supprimer un rapport ne restitue pas le quota ; aucun dépassement n’est facturé. CHF, EUR, USD et GBP sont des tarifs locaux fixes et distincts, sans conversion de devises. Stripe affiche le total taxes incluses avant confirmation. La disponibilité des abonnements est indiquée dans Projects.

## Commencer avec vos mesures

1. Connectez-vous, nommez le projet et sa version, puis importez les mesures JSON décrites dans le [guide Spend Proof](spend-proof.md).
2. Choisissez **Calculer et enregistrer**. L’enregistrement transmet les mesures à ALPNAI pour calcul. La base conserve les résultats agrégés et les libellés, pas les tentatives brutes ni les prompts. N’incluez aucun secret ni identifiant personnel.
3. Enregistrez une autre version, sélectionnez jusqu’à deux rapports et comparez. Téléchargez les détails JSON ou un dossier imprimable.

## Abonnement et factures

Choisissez la devise et la période, acceptez les conditions Projects, puis passez par Stripe. L’accès gratuit ne devient jamais automatiquement payant. L’accès payé commence après confirmation du paiement ; un retour de Stripe ne constitue pas cette preuve. **Abonnement et factures** permet de gérer la facturation et d’arrêter le prochain renouvellement. Un paiement échoué n’accorde aucune nouvelle période. Les rapports existants restent téléchargeables après expiration.

Les achats API/MCP de ce kit restent **exclusivement en sandbox**. Les abonnements Projects sont un service distinct du site ; le kit ne les souscrit ni ne les renouvelle et ne transfère aucune cryptomonnaie.

Assistance : [frederic@alpnor.com](mailto:frederic@alpnor.com).

## Automatiser la livraison de rapports

Une agence qui teste plusieurs agents peut perdre du temps à réunir ses résultats. Ajoutez un appel ALPNAI à la fin de votre propre pipeline : le serveur calcule les coûts, la latence et les contrôles de qualité, puis conserve le résultat dans Projects.

save_project_report calcule et enregistre un rapport dans le projet autorisé explicitement par son titulaire, avec le quota Projects existant. Il attend request_id, title et input. Guide : https://alpnai.com/fr/docs/projects-automation.

Les dépôts automatiques et manuels utilisent ensemble les trois rapports gratuits à vie, ou les 100 rapports de la période mensuelle payée, ou les 1 200 rapports de la période annuelle payée. Il n’y a aucun dépassement facturé et aucun passage automatique à une offre payante.

---

[Votre premier audit](quickstart.md) · [Spend Proof : coût par succès](spend-proof.md)
