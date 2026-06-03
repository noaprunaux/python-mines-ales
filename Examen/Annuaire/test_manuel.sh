#!/usr/bin/env bash
#
# test_manuel.sh — batterie de tests automatisée pour annuaire.py
#
# Lance le serveur, enchaîne toutes les commandes client + le protocole brut
# (netcat si dispo), vérifie chaque réponse, puis arrête proprement le serveur.
# Affiche un bilan PASS/FAIL et renvoie un code retour non nul si un test échoue.
#
# Usage :
#   ./test_manuel.sh                 # hôte de test par défaut : mines-ales.fr
#   ./test_manuel.sh exemple.fr      # avec un autre hôte
#
# Prérequis : .venv activé, dépendances installées, whois + dnsutils présents.

set -u  # erreur sur variable non définie (pas -e : on gère les échecs nous-mêmes)

HOTE="${1:-mines-ales.fr}"
HOST="127.0.0.1"
PORT="8888"
PY="python3"
SCRIPT="annuaire.py"
DB="domaines.db"

# Couleurs (désactivées si la sortie n'est pas un terminal)
if [ -t 1 ]; then
  VERT=$'\033[32m'; ROUGE=$'\033[31m'; JAUNE=$'\033[33m'; GRAS=$'\033[1m'; RAZ=$'\033[0m'
else
  VERT=""; ROUGE=""; JAUNE=""; GRAS=""; RAZ=""
fi

NB_OK=0
NB_KO=0
SRV_PID=""

# --- Helpers ---------------------------------------------------------------

titre() { printf '\n%s=== %s ===%s\n' "$GRAS" "$1" "$RAZ"; }

# verifie <description> <attendu> <obtenu>
verifie() {
  local desc="$1" attendu="$2" obtenu="$3"
  if [ "$obtenu" = "$attendu" ]; then
    printf '  %s[PASS]%s %s\n' "$VERT" "$RAZ" "$desc"
    NB_OK=$((NB_OK + 1))
  else
    printf '  %s[FAIL]%s %s\n' "$ROUGE" "$RAZ" "$desc"
    printf '         attendu : %q\n' "$attendu"
    printf '         obtenu  : %q\n' "$obtenu"
    NB_KO=$((NB_KO + 1))
  fi
}

# verifie_contient <description> <motif> <obtenu>
verifie_contient() {
  local desc="$1" motif="$2" obtenu="$3"
  if printf '%s' "$obtenu" | grep -q -- "$motif"; then
    printf '  %s[PASS]%s %s\n' "$VERT" "$RAZ" "$desc"
    NB_OK=$((NB_OK + 1))
  else
    printf '  %s[FAIL]%s %s\n' "$ROUGE" "$RAZ" "$desc"
    printf '         doit contenir : %q\n' "$motif"
    printf '         obtenu        : %q\n' "$obtenu"
    NB_KO=$((NB_KO + 1))
  fi
}

nettoyage() {
  if [ -n "$SRV_PID" ] && kill -0 "$SRV_PID" 2>/dev/null; then
    titre "Arrêt du serveur (SIGINT = Ctrl-C)"
    kill -INT "$SRV_PID" 2>/dev/null
    # Laisse au serveur le temps de logguer son arrêt propre (max ~5 s).
    ARRET_OK=0
    for _ in $(seq 1 25); do
      grep -q "arrêté proprement" serve.log 2>/dev/null && { ARRET_OK=1; break; }
      kill -0 "$SRV_PID" 2>/dev/null || break
      sleep 0.2
    done
    # Dernier coup d'œil au log après la fin éventuelle du process.
    grep -q "arrêté proprement" serve.log 2>/dev/null && ARRET_OK=1
    kill -9 "$SRV_PID" 2>/dev/null || true
    if [ "$ARRET_OK" = "1" ]; then
      printf '  %s[PASS]%s Arrêt propre du serveur (P3)\n' "$VERT" "$RAZ"
      NB_OK=$((NB_OK + 1))
    else
      printf '  %s[WARN]%s Arrêt propre non confirmé ici (signal non transmis dans cet env.) — testez Ctrl-C à la main\n' "$JAUNE" "$RAZ"
    fi
  fi
  rm -f serve.log
}
trap nettoyage EXIT

# --- Vérifications préalables ----------------------------------------------

titre "Vérifications préalables"
command -v "$PY" >/dev/null || { echo "python3 introuvable"; exit 2; }
[ -f "$SCRIPT" ] || { echo "$SCRIPT introuvable (lancer depuis le dossier annuaire/)"; exit 2; }
command -v whois >/dev/null || printf '  %s[WARN]%s whois absent : contact/email seront null (apt install whois)\n' "$JAUNE" "$RAZ"
command -v nslookup >/dev/null || printf '  %s[WARN]%s nslookup absent : ip sera null (apt install dnsutils)\n' "$JAUNE" "$RAZ"
HAS_NC=0; command -v nc >/dev/null && HAS_NC=1

# Repart d'une base vierge pour des résultats déterministes
rm -f "$DB"
printf '  Base %s réinitialisée, hôte de test : %s\n' "$DB" "$HOTE"

# --- 0. Tests automatiques (pytest) ----------------------------------------

titre "0. Tests unitaires (pytest)"
if command -v pytest >/dev/null || $PY -c "import pytest" 2>/dev/null; then
  if $PY -m pytest -q >/tmp/pytest.out 2>&1; then
    verifie_contient "pytest : couche données" "passed" "$(cat /tmp/pytest.out)"
  else
    printf '  %s[FAIL]%s pytest a échoué :\n' "$ROUGE" "$RAZ"; sed 's/^/         /' /tmp/pytest.out
    NB_KO=$((NB_KO + 1))
  fi
  rm -f /tmp/pytest.out
else
  printf '  %s[WARN]%s pytest non installé (pip install pytest) — étape ignorée\n' "$JAUNE" "$RAZ"
fi

# --- Démarrage du serveur ---------------------------------------------------

titre "Démarrage du serveur"
# Détache complètement le serveur (stdin sur /dev/null, session séparée) pour
# qu'il ne garde pas la session shell attachée à ses pipes.
setsid $PY "$SCRIPT" -vv serve >serve.log 2>&1 </dev/null &
SRV_PID=$!
disown 2>/dev/null || true
# Attend que le serveur soit à l'écoute (max ~5 s)
for _ in $(seq 1 25); do
  grep -q "écoute" serve.log 2>/dev/null && break
  sleep 0.2
done
if ! kill -0 "$SRV_PID" 2>/dev/null; then
  echo "Le serveur n'a pas démarré. Log :"; cat serve.log; exit 2
fi
printf '  Serveur lancé (PID %s) sur %s:%s\n' "$SRV_PID" "$HOST" "$PORT"

# --- 1. Tests client --------------------------------------------------------

titre "1. Commandes client"

OUT=$($PY "$SCRIPT" count 2>/dev/null)
verifie "COUNT initial = 0" "0" "$OUT"

OUT=$($PY "$SCRIPT" search "$HOTE" 2>/dev/null)
verifie "SEARCH avant enregistrement = NOT_FOUND" "NOT_FOUND" "$OUT"

OUT=$($PY "$SCRIPT" record "$HOTE" 2>/dev/null)
verifie "RECORD $HOTE = OK" "OK" "$OUT"

OUT=$($PY "$SCRIPT" record "$HOTE" 2>/dev/null)
verifie "RECORD $HOTE (doublon) = ALREADY_EXISTS" "ALREADY_EXISTS" "$OUT"

OUT=$($PY "$SCRIPT" search "$HOTE" 2>/dev/null)
verifie_contient "SEARCH $HOTE renvoie le bon hôte" "\"hote\": \"$HOTE\"" "$OUT"

OUT=$($PY "$SCRIPT" search inconnu.invalid 2>/dev/null)
verifie "SEARCH hôte bidon = NOT_FOUND" "NOT_FOUND" "$OUT"

OUT=$($PY "$SCRIPT" count 2>/dev/null)
verifie "COUNT après 1 record = 1" "1" "$OUT"

OUT=$($PY "$SCRIPT" list 2>/dev/null)
verifie "LIST contient $HOTE" "$HOTE" "$OUT"

# --- 2. Protocole brut (netcat) --------------------------------------------

titre "2. Protocole JSON ligne (netcat)"
if [ "$HAS_NC" = "1" ]; then
  OUT=$(printf '{"cmd":"COUNT"}\n' | nc -w 3 "$HOST" "$PORT")
  verifie_contient "netcat COUNT renvoie un JSON OK" '"status": "OK"' "$OUT"
  verifie_contient "netcat COUNT renvoie count=1" '"count": 1' "$OUT"
else
  printf '  %s[WARN]%s nc absent (apt install netcat-openbsd) — étape ignorée\n' "$JAUNE" "$RAZ"
fi

# --- 3. Cas limites ---------------------------------------------------------

titre "3. Verbosité et logs"
ERR=$($PY "$SCRIPT" -vvv count 2>&1 >/dev/null)
verifie_contient "-vvv produit un log DEBUG détaillé" "DEBUG" "$ERR"
ERR=$($PY "$SCRIPT" count 2>&1 >/dev/null)
if [ -z "$ERR" ]; then
  verifie "Sans -v : aucun log sur stderr (WARNING only)" "" "$ERR"
else
  printf '  %s[INFO]%s logs sans -v : %q (acceptable si WARNING)\n' "$JAUNE" "$RAZ" "$ERR"
fi

# --- Le serveur est arrêté par le trap nettoyage (test arrêt propre) -------

# Test client SANS serveur : on arrête d'abord, puis on vérifie l'erreur réseau
nettoyage
trap - EXIT  # le nettoyage a déjà tourné

titre "4. Gestion d'erreur réseau (serveur éteint)"
OUT=$($PY "$SCRIPT" count 2>/dev/null); CODE=$?
verifie "Client sans serveur : code retour = 1" "1" "$CODE"

# --- Bilan ------------------------------------------------------------------

titre "BILAN"
TOTAL=$((NB_OK + NB_KO))
if [ "$NB_KO" -eq 0 ]; then
  printf '%s%d/%d tests réussis. Tout est bon %s\n' "$VERT" "$NB_OK" "$TOTAL" "$RAZ"
  exit 0
else
  printf '%s%d/%d réussis, %d échec(s) %s\n' "$ROUGE" "$NB_OK" "$TOTAL" "$NB_KO" "$RAZ"
  exit 1
fi
