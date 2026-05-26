# Feedback — Atelier 4 (Noa PRUNAUX)

## Respect de la consigne

L'essentiel est rendu :

- `socket.socketpair()` ✓
- `fileno()`, `getsockname()`, `getpeername()` imprimés ✓
- `try/finally` avec `close()` manuel ✓
- Réponse à la question commencée mais **tronquée** : « C'est
  pourquoi les adresses sont vides ('') et ne contiennent » —
  la phrase se termine ici. Il manque la suite. À compléter.

À développer dans ta réponse :

- pourquoi vides : AF_UNIX *anonyme*, aucun `bind` sur un chemin
  de fichier ;
- « anonyme » → pas de nom externe visible, aucun processus
  tiers ne peut s'y connecter par nom ;
- différence avec TCP/IPv4 → un socket TCP `bind((host, port))`
  est *publiquement adressable*.

**`try/finally` au lieu de `with`** : ça marche mais le `with`
est plus court et plus sûr :
```python
with sock1, sock2:
    ...
```
Le `__exit__` du gestionnaire de contexte appelle `close()`
automatiquement, même en cas d'exception non capturée.

## Côté Python (à titre indicatif)

- Lisible et concis.
- Les `'{adresse}'` avec quotes autour de la f-string sont une
  bonne idée pour visualiser la chaîne vide (`''`) — détail
  utile.

---
*Évalué sur le commit `119b0cb` (fichier `atelier_04.py`).*
