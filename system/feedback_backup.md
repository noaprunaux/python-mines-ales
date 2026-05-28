# Feedback — S06/A2 (Backup horodaté, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : `shutil.copytree(src, dst)` vers un dossier
`backup_<YYYYMMDD_HHMMSS>/` créé à côté de la source, avec
horodatage formaté par `datetime.now().strftime("%Y%m%d_%H%M%S")`.

Constat sur ton code :

- ✓ `Path(sys.argv[1])` pour la source
- ✓ horodatage `strftime("%Y%m%d_%H%M%S")` exactement comme demandé
- ✓ `chemin_backup = chemin_source.parent / f"backup_{horodatage}"`
  — placé à côté de la source, format de nom conforme
- ✓ `shutil.copytree(chemin_source, chemin_backup)` — un seul appel,
  copie récursive
- ✓ bonus : comptage des fichiers copiés via `rglob("*")` + `is_file()`
- ✓ affichage final propre (`Backup créé : ...` / `Fichiers copiés : ...`)
- ⚠ pas de validation que `chemin_source.is_dir()` ni de gestion
  du cas où `len(sys.argv) < 2`. Le corrigé lève `NotADirectoryError`
  proprement en début de fonction, et bascule en mode démo
  (`tempfile.TemporaryDirectory`) sans argument.
- ⚠ pas de fonction `backup(source)` extraite. Sur ce volume c'est
  acceptable, mais isoler la logique permet de la tester sans CLI.

---
*Évalué sur le commit `1b88e45` (fichier `system/backup.py`).*
