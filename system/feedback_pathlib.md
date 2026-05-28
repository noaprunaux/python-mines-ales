# Feedback — S04/A4 (Décomposer chemin, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : fonction `decomposer(chemin)` qui renvoie le
tuple `(parent, stem, suffix)` via `pathlib.Path`, et au moins
trois exemples dont un `.tar.gz` et un sans extension.

Constat sur ton code :

- ✓ fonction `decomposer(chemin: str) -> tuple` (annotation de
  type — bonus)
- ✓ usage de `Path(chemin).parent` / `.stem` / `.suffix`
- ✓ quatre exemples couvrant les cas attendus :
    - `/tmp/a.txt` (cas simple)
    - `/var/log/archive.tar.gz` (extension double → `.gz` isolé,
      `archive.tar` dans le stem)
    - `/etc/hosts` (pas d'extension → suffix vide)
    - `/home/noa/documents/rapport.final.pdf` (point dans le nom)
- ✓ affichage aligné avec `f"{chemin:<35} -> ..."` — soigné
- détail : le corrigé annote le retour `tuple[str, str, str]`
  (plus précis que `tuple`). Sans impact à l'exécution.
- détail : pas de `main()` ni de garde `if __name__ == "__main__":`.
  Sur ce volume, c'est sans importance.

---
*Évalué sur le commit `4f0afe5` (fichier `system/pathlib.py`).*
