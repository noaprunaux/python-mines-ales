# Mini-annuaire de domaines (Réseaux & Système — Python)

Un mini-annuaire de domaines accessible en réseau. Pour chaque nom d'hôte
(ex. `mines-ales.fr`), l'application enregistre quatre informations :

- l'**adresse IP** résolue ;
- le **nom d'hôte** (clé primaire) ;
- le **contact** déclaré dans `whois` ;
- l'**adresse email** déclarée dans `whois`.

L'application est livrée comme **un seul script Python** (`annuaire.py`)
lançable en deux modes (serveur ou client) via une CLI unique `argparse`.

## Architecture

```
        CLI (argparse, P5)
        /              \
   Serveur (P3) <--JSON ligne--> Client (P4, sockets bas niveau)
        |
   Couche données (P2 : SQLAlchemy + Pydantic)
        |
   Collecte système (P1 : subprocess nslookup/whois)
```

## Installation

### Prérequis système (Debian/Ubuntu)

L'outil `whois` doit être installé pour la collecte (`nslookup` est en général
déjà présent via `dnsutils`) :

```bash
sudo apt update
sudo apt install whois dnsutils
```

### Dépendances Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`email-validator` est requis par Pydantic pour le type `EmailStr`.
`python-dotenv` est optionnel (un parseur maison prend le relais s'il manque).

## Utilisation

Lancer le serveur dans un terminal :

```bash
python annuaire.py serve
# ou avec plus de logs :
python annuaire.py -vv serve
```

Dans un autre terminal, utiliser le client :

```bash
python annuaire.py record mines-ales.fr   # collecte (IP + whois) puis enregistre
python annuaire.py search mines-ales.fr   # détails du domaine ou NOT_FOUND
python annuaire.py count                  # nombre de domaines enregistrés
python annuaire.py list                   # liste des noms d'hôtes
```

### Verbosité (`-v`)

| Flag    | Niveau              | Usage                                   |
|---------|---------------------|-----------------------------------------|
| (aucun) | WARNING             | sortie minimale (erreurs seulement)     |
| `-v`    | INFO                | commande reçue, résultat                |
| `-vv`   | DEBUG               | parsing whois, framing protocole        |
| `-vvv`  | DEBUG + format complet | timestamp, fichier, ligne, thread    |

Les logs partent sur **stderr**, les résultats sur **stdout** (convention Unix).

### Configuration `.env` (bonus 5.3)

Copier `.env.example` en `.env` pour changer l'adresse/port d'écoute :

```
HOST=0.0.0.0
PORT=9000
```

Valeurs par défaut si aucun `.env` : `127.0.0.1:8888`.

## Choix du protocole — Option C : JSON ligne

Chaque message (requête comme réponse) est un objet JSON UTF-8 terminé par un
unique `\n` (*newline-delimited JSON*).

- **Requêtes** : `{"cmd": "SEARCH", "arg": "mines-ales.fr"}\n`
- **Réponses** : `{"status": "OK", "domaine": {...}}\n`, `{"status": "NOT_FOUND"}\n`,
  `{"status": "ALREADY_EXISTS"}\n`, `{"status": "ERROR", "message": "..."}\n`,
  `{"status": "OK", "count": 3}\n`, `{"status": "OK", "hotes": [...]}\n`.

**Justification.** Le protocole est *structuré* (pas de parsing ad hoc fragile),
se valide naturellement côté serveur, sérialise sans effort le modèle `Domaine`
(4 champs) et reste **lisible et testable à la main** :

```bash
printf '{"cmd":"COUNT"}\n' | nc 127.0.0.1 8888
```

Le seul inconvénient est la verbosité, sans conséquence ici. Le framing
« une ligne = un message » est trivial et robuste car `json.dumps` n'émet
jamais de `\n` à l'intérieur du payload.

### Commandes du protocole

| Commande | Argument | Réponse                                                        |
|----------|----------|----------------------------------------------------------------|
| `SEARCH` | `<hôte>` | `{"status":"OK","domaine":{...}}` ou `{"status":"NOT_FOUND"}`   |
| `RECORD` | `<hôte>` | `ALREADY_EXISTS` si connu ; sinon collecte + insert → `OK` / `ERROR` |
| `COUNT`  | —        | `{"status":"OK","count":<int>}`                                |
| `LIST`   | —        | `{"status":"OK","hotes":[...]}` (noms d'hôtes seulement)        |

## Tests (bonus)

```bash
pip install pytest
python3 -m pytest -q
```

Les tests couvrent la **couche données** (CRUD) en isolation, sur une base
SQLite temporaire, sans dépendre du réseau ni de la collecte système.

## Structure du dépôt

```
annuaire.py        # script principal (serveur + client + CLI)
pyproject.toml     # config pytest (pythonpath)
requirements.txt   # dépendances Python
README.md          # ce fichier
.env.example       # exemple de configuration réseau (bonus)
tests/             # tests pytest de la couche données (bonus)
```
