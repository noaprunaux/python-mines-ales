# Feedback — Atelier 2 (Noa PRUNAUX)

## Respect de la consigne

Bien rempli :

- les trois sockets demandés (TCP, UDP, AF_UNIX),
- `fileno()`, `family.name`, `type.name` imprimés pour chacun,

**Subtilité** : tu crées les sockets **hors** du `with` puis tu
les passes dans un `with socket_tcp, socket_udp, socket_unix:`.
Ça marche (les `__exit__` sont appelés à la sortie), mais la
consigne attend de créer les sockets **dans** le `with` pour que
leur cycle de vie soit délimité par le bloc. La différence est
subtile mais importante : si la création d'un socket lève une
exception, les sockets précédents ne sont pas fermés. Trame
recommandée :

```python
with (socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp,
      socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp,
      socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as ux):
    ...
```

**Point manquant** : la question sur les `fileno()`. À ajouter en
commentaire : descripteur unique attribué par le noyau (le plus
petit entier libre de la table du processus).

## Côté Python (à titre indicatif)

- Code clair, espacé. Les trois blocs `print` sont quasi-
  identiques — une boucle aurait évité la duplication.

---
*Évalué sur le commit `4aed8fa` (fichier `reseau/atelier_02.py`).*
