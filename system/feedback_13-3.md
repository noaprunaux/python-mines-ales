# Feedback — S13 Atelier 3 (Token URL-safe, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : `secrets.token_urlsafe(32)`, écriture/relecture d'un `.env` dans un `tempfile.TemporaryDirectory`, comparaison via `secrets.compare_digest`.

Constat sur ton code :

- ✓ `secrets.token_urlsafe(32)`.
- ✓ `tempfile.TemporaryDirectory()` + `os.path.join(tmpdir, ".env")`.
- ✓ Écriture au format `TOKEN=...\n`.
- ✓ Relecture ligne par ligne avec `partition("=")` et vérification `if cle == "TOKEN"` — propre.
- ✓ Comparaison via `secrets.compare_digest(token, token_lu)`.
- ⚠ `contenu` est affiché à partir de `token[:3]` au lieu de lire le fichier (l'exemple attendu affiche le contenu lu du fichier `.env`). Ça marche mais c'est trompeur si on raisonne sur ce qu'on vient de relire.
- ⚠ `token_lu` n'est initialisé que dans la branche `if cle == "TOKEN"` : si jamais la clé manque on aurait un `NameError`. Mineure dans ce contexte.

C'est conforme sur le fond. Quelques détails d'affichage à peaufiner.

---
*Évalué sur le commit `d7e6061` (fichier `system/13-3.py`).*
