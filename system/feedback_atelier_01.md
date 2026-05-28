# Feedback — S03/A1 (Mini-calculatrice CLI, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : `argparse` avec trois positionnels (deux
`float`, un opérateur restreint via `choices=["+","-","*","/"]`),
et **division par zéro → message sur `stderr` + `sys.exit(1)`**.

Constat sur ton code :

- ✓ trois positionnels typés `float` + opérateur avec `choices`
- ✓ `description=` renseignée, `help=` sur chaque argument
- ✓ division par zéro : `print(..., file=sys.stderr)` puis
  `sys.exit(1)` — exactement le contrat
- ✓ structure `main()` + `if __name__ == "__main__":` propre
- ✓ format de sortie `f"{a} {op} {b} = {resultat}"` conforme

Très bonne copie, rien à redire. Au niveau du style, le corrigé
utilise un `else: # "/"` final au lieu d'un `elif args.operateur
== "/":` — c'est une question de goût, ton choix est plus explicite.

---
*Évalué sur le commit `ecbaa44` (fichier `system/atelier_01.py`).*
