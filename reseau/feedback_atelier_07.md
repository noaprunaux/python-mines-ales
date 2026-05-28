# Feedback — Atelier 7 (Trois lectures du même nombre, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : décoder `b"\x00\x00\x00\x2A"` selon trois
recettes (big-endian, little-endian, octets inversés puis
big-endian), puis vérifier que les lectures 2 et 3 donnent la
même valeur.

Constat sur ton code :

- ✓ trois lectures effectuées, affichées avec des libellés clairs
- ✓ comparaison explicite v2 == v3 avec branche `if/else`
- ✓ affichage des octets bruts (`octets.hex(' ')`) — bonus utile
- ⚠ tu utilises `struct.unpack("!I", ...)` / `struct.unpack("<I", ...)`
  là où le corrigé emploie `int.from_bytes(octets, "big" / "little")`.
  Les deux donnent le même résultat ; `int.from_bytes` est plus
  direct pour un simple décodage d'entier (pas besoin de format
  string, pas besoin d'indexer `[0]` sur le tuple renvoyé). À
  garder en tête pour la suite.
- ⚠ tu ne dis pas **pourquoi** v2 == v3 (manque la phrase sur le
  sens de lecture des octets : little-endian = lire de droite à
  gauche, ce qui revient à inverser physiquement puis lire de
  gauche à droite). C'était la question pédagogique de l'atelier.

---
*Évalué sur le commit `cec93ef` (fichier `reseau/atelier_07.py`).*
