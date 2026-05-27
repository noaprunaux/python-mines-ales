# Feedback — Atelier 5 (Noa PRUNAUX)

## Respect de la consigne

Très bien :

- `recv_ligne(sock)` lit octet par octet, gère EOF (`b""`) et
  `b"\n"` ✓
- délimiteur non inclus ✓
- test avec `socketpair`, envoi correct, deux appels
  `recv_ligne` ✓
- `try/finally` pour fermer les sockets — correct, mais le
  `with` est plus court et plus sûr.

**Réponse au bonus tronquée** : tu dis « c'est inefficace car on
lit un octet à la fois » mais tu ne donnes **pas la structure
d'optimisation** demandée par la consigne. À ajouter :

> Optimisation : un buffer (`bytearray`) accumulé entre les
> appels, alimenté par `recv(4096)`. On cherche `\n` avec
> `.find()` dans le buffer, on découpe et on conserve le
> surplus pour la prochaine ligne.

## Côté Python (à titre indicatif)

- Structure : `recv_ligne` + `main` + garde — bonne pratique.
- Docstring de fonction présent.
- Style propre.

---
*Évalué sur le commit `4aed8fa` (fichier `reseau/atelier_05.py`).*
