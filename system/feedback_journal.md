# Feedback — S05/A3 (Journal horodaté, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : ouvrir un fichier journal en mode **append**
(`"a"`) et y écrire une ligne horodatée à chaque appel.

Constat sur ton code :

- ✓ mode `"a"` : append sans écraser le contenu précédent
- ✓ `with open(...)` : fermeture automatique
- ✓ horodatage via `datetime.now().isoformat(timespec="seconds")`
  — format ISO 8601, lisible et triable
- ✓ message lu depuis `sys.argv[1]`
- ⚠ pas de validation `len(sys.argv)` ni d'`encoding="utf-8"`
  explicite sur le `open`. Le corrigé encode explicitement (sur
  Linux c'est UTF-8 par défaut, mais sur Windows c'est cp1252 —
  d'où la bonne pratique). C'est un détail mais qui peut piquer.
- ⚠ pas de fonction (`journaliser(chemin, message)`) ni de
  `main()`. Pour 5 lignes c'est tolérable, mais isoler l'écriture
  rend le code testable.
- détail : si `sys.argv[1]` manque, le script plante avec
  `IndexError`. Le corrigé bascule en mode démo quand aucun
  argument n'est fourni.

---
*Évalué sur le commit `0c01d26` (fichier `system/journal.py`).*
