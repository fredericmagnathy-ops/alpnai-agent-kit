# Données et accès

Préparez des traces minimales et choisissez où le calcul doit être effectué.

[Bibliothèque de documentation](README.md) · [Documentation sur le site](https://alpnai.com/fr/docs)

[Français](../fr/security.md) · [English](../en/security.md) · [Deutsch](../de/security.md)

## Calcul dans le navigateur

Les outils locaux calculent avec les traces chargées dans la page. Le contenu des traces n’est pas envoyé à l’API pour effectuer ce calcul. Les exports HTML et JSON sont créés sur votre appareil.

La page peut charger ses ressources et, avec votre accord, mesurer des étapes du parcours. Le calcul local ne signifie pas que tout le site fonctionne hors ligne.

## Calcul par API ou MCP

Avec l’API ou MCP, les traces sont transmises au serveur pour le calcul. Elles ne sont pas enregistrées dans la base applicative de l’audit. Les données du compte, les clés hachées et les reçus du pilote ont un traitement distinct.

Votre infrastructure et l’hébergeur peuvent produire des journaux techniques. N’envoyez donc que les données nécessaires au calcul, même lorsque la réponse indique persisted:false.

## Ce qui appartient dans les traces

Utilisez des identifiants opaques comme task-001. Fournissez les coûts, la variante, la réussite et les durées. Gardez les noms de clients, emails, documents, prompts et réponses détaillées dans votre propre environnement.

Les champs du contrat sont stricts. Ne placez pas de secret dans task_id ou workflow : leur type texte ne les transforme pas en espace de stockage libre.

## Protéger et remplacer une clé

Une clé active permet les appels autorisés pour son compte. Gardez-la côté serveur ou dans votre environnement local ; ne l’ajoutez pas à un dépôt public ni au code d’une page distribuée à vos visiteurs.

Vous pouvez remplacer une clé perdue depuis le parcours prévu ; l’ancienne est révoquée et le budget de test déjà consommé est conservé. Aucun mot de passe MetaMask, aucune clé privée ni phrase de récupération n’est nécessaire pour l’audit.

---

[Précédent: Paiements et mode de test](payments.md)
