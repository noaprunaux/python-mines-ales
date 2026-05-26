# Feedback — Atelier 3 (Noa PRUNAUX)

## Respect de la consigne

L'essentiel fonctionne, mais avec deux problèmes structurels
importants :

- **`socket = socket.socket(...)`** : tu écrases le nom du
  module `socket` par une instance de socket. Ligne 12, le RHS
  utilise encore le module (`socket.AF_INET`, `socket.SOCK_STREAM`)
  parce que la réaffectation a lieu *après* l'évaluation du RHS.
  Mais c'est une bombe à retardement : si tu rajoutes ensuite
  `socket.gethostbyname(...)` ou `socket.timeout`, ça plantera
  avec `AttributeError`. Utiliser un autre nom :
  ```python
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ```

- **Pas de `with`** : tu ouvres le socket et fais un `close()`
  manuel dans `finally`. Le `with` est plus sûr (il ferme même
  si `settimeout` lève une exception) et c'est l'idiome attendu :
  ```python
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.settimeout(1)
      try:
          s.connect(...)
      except ConnectionRefusedError:
          print(...)
  ```

Le reste est correct :

- argparse `--protocole tcp|udp` requis ✓
- TCP : `settimeout(1)` + `ConnectionRefusedError` → message conforme ✓
- UDP : `sendto` + message conforme ✓

## Côté Python (à titre indicatif)

- Le module `argparse` est nommé `lecteur` — c'est une métaphore
  acceptable mais inhabituelle. La convention est `parser`.
- Pas de fonction `main()` ni de garde.

---
*Évalué sur le commit `9e59673` (fichier `atelier_03.py`).*
