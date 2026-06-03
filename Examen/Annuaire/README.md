# Mini-annuaire de domaines

Petit annuaire de domaines qui se parle à travers le réseau. L'idée : tu lui
donnes un nom d'hôte (par exemple `mines-ales.fr`) et il va chercher tout seul
quatre infos qu'il garde en base :

- l'adresse IP du domaine ;
- le nom d'hôte lui-même (c'est la clé, il est unique) ;
- le contact déclaré dans le `whois` ;
- l'adresse email déclarée dans le `whois`.

Tout tient dans un seul fichier Python, `annuaire.py`. Selon la commande que tu
lui passes, il se comporte soit en serveur, soit en client — le tout via une
petite interface en ligne de commande.

## Comment c'est organisé

```
        CLI (argparse)
        /            \
   Serveur  <--- JSON ligne --->  Client (sockets bas niveau)
      |
   Couche données  (SQLAlchemy + Pydantic)
      |
   Collecte système  (nslookup + whois)
```

Le client et le serveur ne partagent rien d'autre que le protocole : ils
pourraient tourner sur deux machines différentes.

## Mise en route

### Côté système (Debian / Ubuntu)

Il faut `whois` pour la collecte. `nslookup` est en général déjà là (sinon il
arrive avec `dnsutils`) :

```bash
sudo apt update
sudo apt install whois dnsutils
```

### Côté Python

On crée un environnement isolé et on installe les dépendances :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Deux remarques sur les dépendances : `email-validator` est tiré par Pydantic
pour valider le type `EmailStr`, et `python-dotenv` est optionnel — si tu ne
l'installes pas, un petit parseur maison prend le relais pour lire le `.env`.

## À l'usage

D'abord on lance le serveur dans un terminal :

```bash
python annuaire.py serve
# ou, si tu veux voir ce qui se passe :
python annuaire.py -vv serve
```

Puis, dans un autre terminal, on lui parle avec le client :

```bash
python annuaire.py record mines-ales.fr   # va chercher IP + whois, puis enregistre
python annuaire.py search mines-ales.fr   # affiche le domaine, ou NOT_FOUND
python annuaire.py count                  # combien de domaines en base
python annuaire.py list                   # la liste des noms d'hôtes
```

### Régler le niveau de bavardage (`-v`)

Plus tu mets de `-v`, plus le programme te raconte ce qu'il fait :

| Flag    | Niveau                 | Ce que tu vois                         |
|---------|------------------------|----------------------------------------|
| (rien)  | WARNING                | quasiment rien, juste les erreurs      |
| `-v`    | INFO                   | les commandes reçues et leur résultat  |
| `-vv`   | DEBUG                  | le détail du parsing whois, le framing |
| `-vvv`  | DEBUG + format complet | en plus : horodatage, fichier, thread  |

Les logs partent sur la sortie d'erreur (`stderr`), pour ne pas se mélanger
avec les résultats qui, eux, sortent sur `stdout`.

### Changer l'adresse ou le port (`.env`)

Par défaut le serveur écoute sur `127.0.0.1:8888`. Pour changer ça, copie
`.env.example` en `.env` et adapte :

```
HOST=0.0.0.0
PORT=9000
```

## Le protocole : du JSON, une ligne par message

J'avais trois options dans le sujet ; j'ai choisi la **C, le JSON ligne**.
Chaque message — qu'il vienne du client ou du serveur — est un objet JSON sur
une seule ligne, terminé par un `\n`.

Côté requête, ça donne par exemple :

```
{"cmd": "SEARCH", "arg": "mines-ales.fr"}
```

Et côté réponse, selon les cas : `{"status": "OK", "domaine": {...}}`,
`{"status": "NOT_FOUND"}`, `{"status": "ALREADY_EXISTS"}`,
`{"status": "OK", "count": 3}`, `{"status": "OK", "hotes": [...]}`, ou
`{"status": "ERROR", "message": "..."}` en cas de pépin.

**Pourquoi ce choix ?** Honnêtement, c'est celui qui m'a paru le plus propre.
Le message est structuré, donc pas de parsing fait main à coups de `split` qui
casse au premier cas tordu. Je peux valider la requête côté serveur sans
effort, et sérialiser mon modèle `Domaine` (ses 4 champs) directement. Bonus
appréciable : ça reste lisible à l'œil nu, donc testable à la main avec
`netcat` :

```bash
printf '{"cmd":"COUNT"}\n' | nc 127.0.0.1 8888
```

Le seul reproche qu'on peut lui faire, c'est d'être un peu verbeux — mais vu la
taille des messages ici, ça ne change rien. Et le découpage « une ligne = un
message » marche bien parce que `json.dumps` ne met jamais de retour à la ligne
au milieu du contenu.

### Les commandes comprises par le serveur

| Commande | Argument | Réponse                                                        |
|----------|----------|----------------------------------------------------------------|
| `SEARCH` | `<hôte>` | le domaine en JSON, ou `NOT_FOUND`                             |
| `RECORD` | `<hôte>` | `ALREADY_EXISTS` si déjà connu ; sinon collecte + insert → `OK` (ou `ERROR`) |
| `COUNT`  | —        | le nombre de domaines enregistrés                              |
| `LIST`   | —        | la liste des noms d'hôtes, rien de plus                        |

## Tester tout ça

### Les tests unitaires

Ils vérifient la couche données (le CRUD) toute seule, sur une base SQLite
jetable — pas besoin de réseau ni de `whois` :

```bash
pip install pytest
python3 -m pytest -q
```

### Le script qui teste tout d'un coup

Pour ne pas avoir à relancer les dix commandes à la main à chaque fois, j'ai
écrit un petit script bash, `test_manuel.sh`. Il fait tout le boulot : il lance
les tests unitaires, démarre le serveur en arrière-plan, enchaîne toutes les
commandes client (record, search, count, list, le cas du doublon, l'hôte
inconnu…), teste le protocole brut avec `netcat`, vérifie les niveaux de logs,
contrôle que le client réagit bien quand le serveur est éteint, puis arrête le
serveur proprement. À la fin il affiche un bilan clair avec le compte des
tests réussis.

```bash
chmod +x test_manuel.sh
./test_manuel.sh                 # teste avec mines-ales.fr
./test_manuel.sh github.com      # ou un autre hôte de ton choix
```

Si `whois` ou `netcat` ne sont pas installés, le script ne plante pas : il
saute simplement l'étape concernée en l'indiquant.

## Ce qu'il y a dans le dépôt

```
annuaire.py        le programme (serveur + client + CLI)
test_manuel.sh     le script qui teste tout automatiquement
tests/             les tests unitaires de la couche données
pyproject.toml     config pytest (pour que l'import marche)
requirements.txt   les dépendances Python
.env.example       exemple de config réseau
README.md          ce fichier
```
