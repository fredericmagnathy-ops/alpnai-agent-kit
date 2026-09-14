# Import CSV pour ALPNAI

[English](README.md) · [Deutsch](README.de.md)

Transformez un export de tentatives en JSON utilisable par **Spend Proof, Latency Lab et Quality Gate**. Python 3.10 ou supérieur ; aucune dépendance à installer. La conversion est entièrement locale. Aucun compte, clé ni appel réseau n’est nécessaire.

## Essayer en une minute

Depuis ce dossier :

```sh
mkdir -p .alpnai
python3 csv_to_alpnai.py --input fixtures/attempts.synthetic.csv --output .alpnai/exemple.json
```

Le fichier contient **des données fictives** : 10 tentatives, 4 tâches par variante, 2 reprises au total, toutes les durées renseignées. Le moteur calcule 0,18 USD pour la référence et 0,09 USD pour la variante, 3 tâches réussies sur 4 de chaque côté, et un P95 enregistré de 3 200 / 1 800 ms. Ces valeurs vérifient le calcul ; elles ne représentent aucune économie client. Avec seulement 4 tâches par variante, la décision par défaut reste `collect_more_data`.

Remplacez ensuite `--input` par votre export et choisissez un nouveau nom de sortie. Les fichiers existants ne sont jamais écrasés. Le terminal affiche seulement des compteurs et les erreurs de format ; le JSON contient vos identifiants et mesures. Les nouveaux fichiers sont créés avec des permissions `0600` sur les systèmes compatibles.

## Ce que doit représenter une ligne

**Une ligne = une tentative complète d’une tâche.** Gardez chaque tentative échouée et chaque reprise, avec son coût et sa durée propres. Une ligne ne doit pas représenter un appel fournisseur isolé si la tentative en comprend plusieurs : agrégez d’abord les appels de cette tentative dans votre télémétrie. Ne transformez pas un total de reprises en lignes inventées.

| Colonne | Valeur attendue |
|---|---|
| `task_id` | Identifiant opaque stable de tâche ; mêmes identifiants dans les deux variantes. 1 à 128 unités UTF-16. |
| `workflow` | Nom du processus, 1 à 80 unités UTF-16. Un `task_id` ne peut pas appartenir à plusieurs processus. |
| `variant` | Exactement `baseline` ou `candidate`. |
| `cost_usd` | Coût complet enregistré de **cette tentative**, en USD : modèles, outils, recherche et autres appels. Nombre positif ou nul, au plus 10 000 USD et six décimales. |
| `success` | `true` / `false` (casse indifférente) ou `1` / `0`, selon votre évaluation du résultat. Un code HTTP 200 ne prouve pas la réussite de la tâche. |
| `latency_ms` | Facultatif : durée enregistrée de la tentative en millisecondes, de 0 à 86 400 000. Une cellule vide reste manquante. |
| `attempt_id` | Facultatif : identifiant propre à chaque tentative d’une même tâche et variante ; 1 à 256 unités UTF-16. Les doublons provoquent une erreur. Cette colonne n’est pas envoyée dans le JSON. |

Les identifiants refusent les espaces en début/fin et les caractères de contrôle. Les noms de colonnes sont sensibles à la casse. Les autres colonnes sont ignorées et exclues du JSON ; ne placez aucun prompt, document ou secret dans les champs retenus.

Le convertisseur **n’invente aucun prix, ne convertit aucune devise et n’estime aucun coût à partir de tokens**. Si vous n’avez que des tokens, fournissez d’abord les coûts mesurés dans votre système. Les valeurs utilisent un point décimal, y compris dans un CSV à point-virgule. Les fractions de micro-USD sont rejetées sans arrondi : agrégez vos frais correctement en amont.

ALPNAI regroupe les lignes par `workflow`, `variant`, `task_id`. Une tâche est réussie si au moins une tentative est réussie ; tous ses coûts comptent. Le P95 utilise la somme des durées enregistrées des tentatives par tâche. Cette somme ne mesure pas la durée réelle d’opérations parallèles. Une durée manquante empêche un P95 complet pour la variante concernée.

## Adapter les colonnes d’un export existant

`--map CHAMP=COLONNE` associe un champ ALPNAI à votre en-tête CSV. Pour un nom contenant des espaces, mettez toute l’association entre guillemets. Cet exemple peut être exécuté tel quel :

```sh
python3 csv_to_alpnai.py --input fixtures/export.synthetic.csv --output .alpnai/export-adapte.json --delimiter ';' --map task_id=job_id --map workflow=pipeline --map variant=arm --map cost_usd=measured_usd --map success=passed --map latency_ms=duration_ms --map attempt_id=request_id
```

Les séparateurs acceptés sont la virgule (défaut), `;` et `tab`. Le fichier doit être en UTF-8 ; le BOM UTF-8 est accepté. Maximum local : 2 Mio de CSV ; limites ALPNAI : 1 000 tentatives et 512 000 octets UTF-8 pour le JSON. Si nécessaire, séparez des ensembles complets de tâches en gardant ensemble chaque tâche, toutes ses reprises et les deux variantes.

Sans `attempt_id`, les lignes identiques sont conservées et signalées : elles peuvent être de vraies reprises ou des doublons de télémétrie. Vérifiez l’export source. Le programme ne les déduplique jamais silencieusement.

## Utiliser le résultat

**Navigateur :** ouvrez [Spend Proof](https://alpnai.com/fr/tools/spend-proof), [Latency Lab](https://alpnai.com/fr/tools/latency-lab) ou [Quality Gate](https://alpnai.com/fr/tools/quality-gate) et collez le contenu du JSON dans le champ des données. Le calcul du navigateur est local. L’enregistrement dans Projects est une action distincte qui transmet les données au service.

**Kit Python :** depuis la racine du [kit ALPNAI](https://github.com/fredericmagnathy-ops/alpnai-agent-kit), fournissez une clé active via le gestionnaire de secrets dans `ALPNAI_AGENT_KEY`, puis indiquez les chemins réels de votre JSON et d’un nouveau rapport :

```sh
python3 examples/audit.py --input /chemin/prive/mes-tentatives.json --report /chemin/prive/mon-rapport.json
```

Cette commande transmet les traces à `POST /api/v1/spend-proof` avec authentification Bearer. L’audit est gratuit et renvoie `payment_required:false` et `persisted:false` ; il ne sauvegarde pas votre rapport dans Projects. Les autres API gratuites acceptent le même JSON : `POST /api/v1/latency` et `POST /api/v1/quality-gate`. Le client `audit.py` reste dédié à Spend Proof.

Les mêmes identifiants, une définition commune du succès et au moins 30 tâches distinctes par variante sont requis par défaut pour une comparaison. Un import réussi ne prouve ni la complétude des factures ni la qualité du jeu d’essai. Il n’autorise aucun déploiement automatique.

## Seuils facultatifs et vérification

`--config fixtures/config.example.json` ajoute les seuils explicites du fichier : 30 tâches minimum, réussite minimum de 95 %, baisse maximum de 2 points, P95 maximum de 3 000 ms. Adaptez ce plafond à votre usage. Les seuils restent absents du JSON sans cette option ; le moteur applique ses valeurs par défaut. `monthlyTasks` peut être ajouté pour un unique processus et désigne les tâches de référence lancées par mois. La projection éventuelle reste conditionnelle.

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

20 tests hors réseau vérifient les valeurs, les reprises, les erreurs, les mappings, les limites et les fichiers. Pour vérifier le client réel du kit, en remplaçant le chemin :

```sh
python3 tests/check_kit_command.py --kit /chemin/vers/alpnai-agent-kit
```

