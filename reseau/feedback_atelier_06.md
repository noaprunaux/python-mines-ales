# Feedback — Atelier 6 (Noa PRUNAUX)

## Respect de la consigne

Très bien :

- `recv_exactement(sock, n)` correct, gère `recv` partiels et
  EOF ✓
- `envoyer_message` : préfixe 4 octets big-endian, envoyé en
  deux `sendall` séparés (correct) ✓
- `recevoir_message` : lit 4 octets, décode, lit la quantité ✓
- test avec `socketpair`, 3 messages, **comparaison explicite**
  avec affichage `Identique à l'original / Différent` ✓

Détail : tu lèves `RuntimeError` au lieu de `ConnectionError`
dans `recv_exactement`. `ConnectionError` est plus précis
sémantiquement (c'est une erreur de connexion), et c'est ce que
fait le corrigé. `RuntimeError` est plus générique.

Tu fais aussi deux `sendall` séparés (`entete` puis `message`)
au lieu d'un seul `sendall(entete + message)`. Les deux marchent ;
le corrigé fait un seul appel pour réduire les syscalls.

## Côté Python (à titre indicatif)

- Structure : 3 fonctions + `main` + garde — bonne pratique.
- Docstrings de fonctions — bonne pratique.
- `try/finally` au lieu de `with` — `with` plus court et plus
  sûr.

---
*Évalué sur le commit `4aed8fa` (fichier `reseau/atelier_06.py`).*
