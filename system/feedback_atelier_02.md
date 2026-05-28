# Feedback — S01/A2 (Phrase formatée, PRUNAUX Noa)

## Respect de la consigne

Critères attendus : demander prénom + âge, calculer l'année de
naissance via `date.today().year - age`, afficher une f-string,
et **gérer `ValueError`** lors du `int()` de l'âge.

Constat sur ton code :

- ✓ saisie du prénom et de l'âge avec `input`
- ✓ calcul `annee = date - int(age)` correct
- ✓ phrase finale en f-string conforme à l'attendu
- ⚠ **pas de gestion de `ValueError`** sur `int(age)` : si
  l'utilisateur tape « vingt » ou laisse vide, le script plante
  avec une trace Python. Le corrigé encapsule la saisie dans une
  petite fonction `lire_entier(invite)` avec un `try/except
  ValueError` qui redemande tant que c'est invalide.
- ⚠ tu utilises `datetime.now().year` au lieu de `date.today().year`.
  Les deux marchent ; `date.today()` est plus précis sémantiquement
  (tu veux une date, pas un instant) et c'est ce que demande
  l'énoncé.
- ⚠ pas de fonction `main()` ni de garde `if __name__ == "__main__":`
  — sur 7 lignes c'est tolérable, mais bonne pratique à prendre.
- détail : `prénom` avec un accent est valide en Python 3 mais
  inhabituel ; la convention reste `prenom` (ASCII).

---
*Évalué sur le commit `3bba66c` (fichier `system/atelier_02.py`).*
