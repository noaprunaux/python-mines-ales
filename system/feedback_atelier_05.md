# Feedback — S03/A5 (Convertisseur de température, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : `argparse` avec `--from` et `--to` (mots-clés
Python → utiliser `dest="depuis"` / `dest="vers"`),
`choices=["celsius","fahrenheit","kelvin"]`, et conversion
**en passant systématiquement par le Celsius** (pas de table
directe F↔K).

Constat sur ton code :

- ✓ `--from` avec `dest="depuis"` et `--to` avec `dest="vers"`
  — exactement la subtilité visée
- ✓ `choices=["celsius","fahrenheit","kelvin"]` sur les deux
- ✓ `required=True` sur `--from` et `--to`
- ✓ **pivot Celsius** : tu convertis d'abord vers Celsius
  (`en_celsius`), puis depuis Celsius vers la cible. Aucune
  formule directe F↔K. C'est précisément ce que demande l'atelier.
- ✓ bonus `--precision` avec valeur par défaut `2`, appliquée à
  la fois à `valeur` et à `resultat` via `f"{x:.{p}f}"`
- ✓ court-circuit `if args.depuis == args.vers: resultat = args.valeur`
  — petit bonus de performance
- détail : le corrigé extrait les conversions dans deux fonctions
  `vers_celsius(valeur, echelle)` et `depuis_celsius(valeur, echelle)`
  pour mieux séparer les responsabilités. Sur ton volume de code
  les `if/elif` en ligne sont tout à fait acceptables.

---
*Évalué sur le commit `d9121a3` (fichier `system/atelier_05.py`).*
