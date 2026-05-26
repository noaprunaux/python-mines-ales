# Feedback — Atelier 1 (Noa PRUNAUX)

## Respect de la consigne

Le contrat est rempli :

- argument CLI lu,
- IPv4 et IPv6 séparées dans deux listes,
- déduplication par `if adresse not in ipv4`,
- total cohérent : `len(ipv4) + len(ipv6)`,
- format de sortie conforme à l'exemple (`IPv4 : ...`).

Très bonne copie sur le fond.

## Côté réseau

- Tu as bien identifié que `getaddrinfo` peut renvoyer des doublons,
  et tu les filtres explicitement — c'est exactement l'idée
  pédagogique de l'atelier.
- Le dépaquetage `famille = info[0]`, `adresse = info[4][0]`
  fonctionne. Plus lisible avec le tuple nommé :
  ```python
  for famille, _t, _p, _c, sockaddr in enregistrements:
      adresse = sockaddr[0]
  ```
- Alternative pour la dédup : utiliser un `set()` au lieu d'une
  liste. La complexité passe de O(n) à O(1) pour `in`. Pour ce
  volume ça ne change rien, mais c'est l'idiome Python.

## Côté Python (à titre indicatif)

- Pas de fonction `main()` ni de garde
  `if __name__ == "__main__":`. Sur 28 lignes c'est tolérable.
- Pas de gestion d'erreur (`socket.gaierror`) ni de validation
  `len(sys.argv)` — un domaine inexistant ou un appel sans argument
  fera planter le script.
- Code lisible, bien aéré.

---
*Évalué sur le commit `9e59673` (fichier `atelier_01.py`).*
