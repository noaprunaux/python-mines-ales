# Feedback — S07/A3 (Extraction tar.gz sécurisée, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : créer une archive `.tar.gz` factice dans un
dossier temporaire, l'extraire dans une cible avec
`tar.extractall(cible, filter="data")`, et lister les fichiers
extraits.

Constat sur ton code :

- ✗ **Erreur de syntaxe bloquante ligne 6** :
  ```python
  $dossier_temporaire = Path(tempfile.mkdtemp())
  ```
  Le `$` n'est **pas** un caractère valide en Python (c'est une
  syntaxe shell ou PHP, pas Python). Le script ne compile pas du
  tout — `python3 -c "import ast; ast.parse(open('targz.py').read())"`
  renvoie `SyntaxError`. Donc rien de ce qui suit n'a été exécuté.
  À corriger : retirer le `$`.

Une fois ce `$` retiré, le reste du fichier est correct :

- ✓ création d'un dossier temporaire avec `tempfile.mkdtemp()`
  (le corrigé utilise plutôt `tempfile.TemporaryDirectory()` dans
  un `with`, qui nettoie automatiquement à la sortie — sinon le
  dossier reste sur le disque)
- ✓ trois fichiers factices écrits via `write_text`
- ✓ création de l'archive avec `tarfile.open(..., "w:gz")` + `tar.add`
- ✓ extraction avec `tar.extractall(dossier_cible, filter="data")`
  — c'est exactement le point pédagogique de l'atelier (le
  `filter="data"` bloque les chemins absolus et les liens
  malveillants)
- ✓ listage final via `rglob("*")` + `is_file()`
- ⚠ `tempfile.mkdtemp()` ne supprime rien : à chaque exécution,
  un nouveau dossier reste dans `/tmp`. Avec
  `tempfile.TemporaryDirectory()` dans un `with`, tout est nettoyé.
- ⚠ `dossier_cible = Path("cible")` crée le dossier dans le
  répertoire courant — ça pollue le cwd. Le corrigé met `cible/`
  **dans** le dossier temporaire pour rester confiné.
- ⚠ pas de fonction `main()` ni de garde.

Verdict : l'intention est bonne et l'usage de `filter="data"` est
là, mais le `$` rend le code non exécutable en l'état. À corriger
en priorité.

---
*Évalué sur le commit `3696ad8` (fichier `system/targz.py`).*
