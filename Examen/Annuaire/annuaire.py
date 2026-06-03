#!/usr/bin/env python3
"""Mini-annuaire de domaines accessible en réseau.

Ce script unique se lance en deux modes via une CLI argparse :
  - ``serve``  : démarre le serveur d'application (socketserver threadé) ;
  - ``search``/``record``/``count``/``list`` : agissent comme client réseau.

PROTOCOLE CHOISI — Option C : JSON ligne.
    Chaque message (requête comme réponse) est un objet JSON UTF-8 terminé par
    un unique '\\n' (newline-delimited JSON). Requête : {"cmd": "...", "arg": "..."}.
    Justification : le protocole est *structuré* (pas de parsing ad hoc fragile),
    se valide naturellement avec Pydantic côté serveur, sérialise sans effort le
    modèle ``Domaine`` (4 champs) et reste lisible/testable à la main (netcat,
    `echo '{"cmd":"COUNT"}' | nc ...`). Le seul surcoût est la verbosité, sans
    conséquence ici. Le framing « une ligne = un message » est trivial et
    robuste tant que les payloads ne contiennent pas de '\\n' (garanti par
    json.dumps sur une seule ligne).

Modules/compétences couverts : subprocess (S08), pathlib (S04), Pydantic v2,
SQLAlchemy ORM, socketserver ThreadingMixIn+TCPServer (R03), sockets bas niveau
(R00), argparse (S03), logging, .env (S13/bonus).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import re
import socket
import socketserver
import subprocess
import sys
from pathlib import Path

from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy import String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Configuration (.env — bonus 5.3)
# ----------------------------------------------------------------------------
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888


def charger_env(chemin: Path | None = None) -> None:
    """Charge un fichier .env dans os.environ sans écraser les variables déjà
    définies. Utilise python-dotenv si disponible, sinon un parseur maison
    minimal (style S13/A3 : lignes KEY=VALUE, # commentaires ignorés)."""
    chemin = chemin or (Path(__file__).resolve().parent / ".env")
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=chemin, override=False)
        logger.debug("Configuration chargée via python-dotenv (%s)", chemin)
        return
    except ImportError:
        pass

    if not chemin.exists():
        logger.debug(".env absent (%s), valeurs par défaut utilisées", chemin)
        return

    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, _, valeur = ligne.partition("=")
        cle, valeur = cle.strip(), valeur.strip().strip('"').strip("'")
        os.environ.setdefault(cle, valeur)
    logger.debug("Configuration chargée via parseur maison (%s)", chemin)


def config_reseau() -> tuple[str, int]:
    """Retourne (host, port) depuis l'environnement, avec valeurs par défaut."""
    host = os.environ.get("HOST", DEFAULT_HOST)
    try:
        port = int(os.environ.get("PORT", DEFAULT_PORT))
    except ValueError:
        logger.warning("PORT invalide dans .env, repli sur %d", DEFAULT_PORT)
        port = DEFAULT_PORT
    return host, port


# ============================================================================
# PARTIE 1 — Collecte d'informations (subprocess + parsing)
# ============================================================================
_RE_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_RE_EMAIL = re.compile(r"\S+@\S+")


def resoudre_ip(hote: str) -> str | None:
    """Résout l'IPv4 d'un hôte de façon cross-platform via nslookup.

    Détecte l'OS (informatif), appelle ``nslookup`` avec capture de la sortie
    et un timeout, puis extrait la première IPv4 figurant *après* la requête
    initiale (la sortie nslookup commence par l'adresse du serveur DNS, qu'il
    faut donc ignorer). Retourne None en cas d'échec (code non nul, timeout,
    outil absent).
    """
    systeme = platform.system()
    logger.debug("resoudre_ip(%r) sur OS=%s", hote, systeme)
    try:
        proc = subprocess.run(
            ["nslookup", hote],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except FileNotFoundError:
        logger.warning("nslookup introuvable sur ce système")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("nslookup a expiré (timeout) pour %s", hote)
        return None

    if proc.returncode != 0:
        logger.debug("nslookup code retour %d pour %s", proc.returncode, hote)
        return None

    # La sortie type contient :
    #   Server:  192.168.1.1          <- serveur DNS (à ignorer)
    #   Address: 192.168.1.1#53
    #   Non-authoritative answer:
    #   Name:    example.com
    #   Address: 142.250.179.110      <- IP voulue
    lignes = proc.stdout.splitlines()
    debut = 0
    for i, ligne in enumerate(lignes):
        if "answer" in ligne.lower() or ligne.lower().startswith("name:"):
            debut = i
            break
    for ligne in lignes[debut:]:
        if "address" in ligne.lower():
            m = _RE_IPV4.search(ligne)
            if m:
                ip = m.group(0)
                logger.debug("IP résolue pour %s : %s", hote, ip)
                return ip
    # Repli : première IPv4 trouvée après la moitié de la sortie.
    for ligne in lignes[debut:]:
        m = _RE_IPV4.search(ligne)
        if m:
            return m.group(0)
    logger.debug("Aucune IPv4 extraite pour %s", hote)
    return None


def interroger_whois(hote: str) -> tuple[str | None, str | None]:
    """Interroge ``whois`` et retourne (contact, email).

    contact = "Registrant Name" (ou "Registrant:") ; email = premier match
    \\S+@\\S+. Retourne (None, None) en cas d'échec.
    """
    logger.debug("interroger_whois(%r)", hote)
    try:
        proc = subprocess.run(
            ["whois", hote],
            capture_output=True,
            text=True,
            timeout=10.0,
        )
    except FileNotFoundError:
        logger.warning("whois introuvable (apt install whois)")
        return None, None
    except subprocess.TimeoutExpired:
        logger.warning("whois a expiré (timeout) pour %s", hote)
        return None, None

    if proc.returncode != 0 and not proc.stdout:
        logger.debug("whois code retour %d pour %s", proc.returncode, hote)
        return None, None

    sortie = proc.stdout
    contact: str | None = None
    email: str | None = None

    for ligne in sortie.splitlines():
        bas = ligne.lower().strip()
        if contact is None and (
            bas.startswith("registrant name") or bas.startswith("registrant:")
        ):
            _, _, valeur = ligne.partition(":")
            valeur = valeur.strip()
            if valeur:
                contact = valeur

    m = _RE_EMAIL.search(sortie)
    if m:
        email = m.group(0).strip().strip(".,;)")

    logger.debug("whois %s -> contact=%r email=%r", hote, contact, email)
    return contact, email


# ----------------------------------------------------------------------------
# 1.3 — Modèle Pydantic et fonction de synthèse
# ----------------------------------------------------------------------------
class Domaine(BaseModel):
    """Représentation validée d'un enregistrement de domaine."""

    hote: str
    ip: str | None = None
    contact: str | None = None
    email: EmailStr | None = None


def collecter(hote: str) -> Domaine:
    """Combine résolution IP (1.1) et whois (1.2) en une instance Domaine."""
    ip = resoudre_ip(hote)
    contact, email = interroger_whois(hote)
    # Si l'email extrait n'est pas valide pour EmailStr, on retombe sur None
    # plutôt que de faire échouer toute la collecte.
    try:
        return Domaine(hote=hote, ip=ip, contact=contact, email=email)
    except ValidationError:
        logger.debug("Email %r invalide pour %s, ignoré", email, hote)
        return Domaine(hote=hote, ip=ip, contact=contact, email=None)


# ============================================================================
# PARTIE 2 — Persistance (SQLAlchemy ORM + SQLite)
# ============================================================================
BDD_PATH = Path(__file__).resolve().parent / "domaines.db"


class Base(DeclarativeBase):
    pass


class DomaineORM(Base):
    """Table ``domaines`` — mêmes 4 champs, clé primaire = hote."""

    __tablename__ = "domaines"

    hote: Mapped[str] = mapped_column(String, primary_key=True)
    ip: Mapped[str | None] = mapped_column(String, nullable=True)
    contact: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)


# Engine + factory de sessions. ``check_same_thread=False`` car le serveur est
# threadé (P3) : chaque requête peut s'exécuter dans un thread différent.
engine = create_engine(
    f"sqlite:///{BDD_PATH}",
    connect_args={"check_same_thread": False},
)
Session = sessionmaker(bind=engine)


def init_bdd() -> None:
    """Crée les tables au démarrage si elles n'existent pas."""
    Base.metadata.create_all(engine)
    logger.debug("Base initialisée : %s", BDD_PATH)


def _orm_vers_pydantic(obj: DomaineORM) -> Domaine:
    return Domaine(hote=obj.hote, ip=obj.ip, contact=obj.contact, email=obj.email)


# ----------------------------------------------------------------------------
# 2.3 — Fonctions CRUD (entrée/sortie en modèles Pydantic ; l'ORM reste interne)
# ----------------------------------------------------------------------------
def enregistrer(domaine: Domaine) -> None:
    """INSERT d'un domaine. Lève ValueError si l'hôte est déjà présent."""
    with Session() as session:
        obj = DomaineORM(
            hote=domaine.hote,
            ip=domaine.ip,
            contact=domaine.contact,
            email=str(domaine.email) if domaine.email else None,
        )
        session.add(obj)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValueError(f"{domaine.hote} déjà enregistré") from exc
    logger.info("Domaine enregistré : %s", domaine.hote)


def lister() -> list[Domaine]:
    """Retourne tous les enregistrements (liste de modèles Pydantic)."""
    with Session() as session:
        objs = session.scalars(select(DomaineORM).order_by(DomaineORM.hote)).all()
        return [_orm_vers_pydantic(o) for o in objs]


def chercher(hote: str) -> Domaine | None:
    """Recherche par clé primaire ; None si absent."""
    with Session() as session:
        obj = session.get(DomaineORM, hote)
        return _orm_vers_pydantic(obj) if obj else None


def compter() -> int:
    """Nombre de domaines enregistrés."""
    with Session() as session:
        return len(session.scalars(select(DomaineORM.hote)).all())


# ============================================================================
# PARTIE 3 — Serveur d'application (socketserver, protocole JSON ligne)
# ============================================================================
class AnnuaireHandler(socketserver.StreamRequestHandler):
    """Traite une connexion : lit des requêtes JSON ligne et répond en JSON ligne.

    Une connexion peut enchaîner plusieurs commandes (une par ligne) jusqu'à la
    fermeture du client.
    """

    def _repondre(self, obj: dict) -> None:
        donnees = (json.dumps(obj) + "\n").encode("utf-8")
        self.wfile.write(donnees)
        self.wfile.flush()

    def handle(self) -> None:  # noqa: C901 — dispatch lisible malgré sa taille
        adresse = self.client_address
        logger.info("Connexion de %s", adresse)
        for brut in self.rfile:  # itère ligne par ligne (framing '\n')
            ligne = brut.decode("utf-8", errors="replace").strip()
            if not ligne:
                continue
            logger.debug("Reçu de %s : %s", adresse, ligne)
            try:
                requete = json.loads(ligne)
                cmd = str(requete.get("cmd", "")).upper()
                arg = requete.get("arg")
            except json.JSONDecodeError:
                self._repondre({"status": "ERROR", "message": "JSON invalide"})
                continue

            logger.info("Commande %s arg=%r de %s", cmd, arg, adresse)
            try:
                self._dispatch(cmd, arg)
            except Exception as exc:  # robustesse : ne jamais tuer le thread
                logger.exception("Erreur en traitant %s", cmd)
                self._repondre({"status": "ERROR", "message": str(exc)})

    def _dispatch(self, cmd: str, arg) -> None:
        if cmd == "SEARCH":
            if not arg:
                self._repondre({"status": "ERROR", "message": "arg requis"})
                return
            dom = chercher(arg)
            if dom is None:
                self._repondre({"status": "NOT_FOUND"})
            else:
                self._repondre({"status": "OK", "domaine": dom.model_dump(mode="json")})

        elif cmd == "RECORD":
            if not arg:
                self._repondre({"status": "ERROR", "message": "arg requis"})
                return
            if chercher(arg) is not None:
                self._repondre({"status": "ALREADY_EXISTS"})
                return
            try:
                dom = collecter(arg)  # peut être long (whois) -> threading utile
                enregistrer(dom)
            except Exception as exc:
                self._repondre({"status": "ERROR", "message": str(exc)})
                return
            self._repondre({"status": "OK", "domaine": dom.model_dump(mode="json")})

        elif cmd == "COUNT":
            self._repondre({"status": "OK", "count": compter()})

        elif cmd == "LIST":
            hotes = [d.hote for d in lister()]
            self._repondre({"status": "OK", "hotes": hotes})

        else:
            self._repondre({"status": "ERROR", "message": f"commande inconnue: {cmd}"})


class ServeurThreade(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Mixin en premier : chaque connexion est traitée dans son propre thread."""

    allow_reuse_address = True
    daemon_threads = True


def lancer_serveur(host: str, port: int) -> None:
    """Démarre le serveur threadé avec arrêt propre sur Ctrl-C."""
    init_bdd()
    with ServeurThreade((host, port), AnnuaireHandler) as serveur:
        logger.warning("Serveur à l'écoute sur %s:%d (Ctrl-C pour arrêter)", host, port)
        try:
            serveur.serve_forever()
        except KeyboardInterrupt:
            logger.warning("Arrêt demandé (Ctrl-C)")
        finally:
            serveur.shutdown()
            logger.warning("Serveur arrêté proprement")


# ============================================================================
# PARTIE 4 — Client réseau (sockets bas niveau)
# ============================================================================
class ErreurClient(Exception):
    """Erreur applicative renvoyée par le serveur ou problème réseau."""


def recv_ligne(sock: socket.socket) -> str:
    """Lit une ligne complète (jusqu'à '\\n') depuis un socket, octet par octet.

    Pour le protocole JSON ligne : on accumule jusqu'au newline puis on
    json.loads côté appelant. Lève ErreurClient si la connexion se ferme avant
    le '\\n'.
    """
    morceaux: list[bytes] = []
    while True:
        octet = sock.recv(1)
        if not octet:
            if morceaux:
                break
            raise ErreurClient("connexion fermée par le serveur")
        if octet == b"\n":
            break
        morceaux.append(octet)
    return b"".join(morceaux).decode("utf-8", errors="replace")


def _envoyer(host: str, port: int, requete: dict, timeout: float = 15.0) -> dict:
    """Ouvre une connexion, envoie une requête JSON ligne, lit la réponse."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            payload = (json.dumps(requete) + "\n").encode("utf-8")
            logger.debug("Envoi -> %s:%d : %s", host, port, requete)
            sock.sendall(payload)
            ligne = recv_ligne(sock)
    except ConnectionRefusedError as exc:
        raise ErreurClient(f"connexion refusée ({host}:{port}) — serveur lancé ?") from exc
    except socket.timeout as exc:
        raise ErreurClient("délai dépassé en attendant le serveur") from exc

    logger.debug("Reçu <- %s", ligne)
    try:
        reponse = json.loads(ligne)
    except json.JSONDecodeError as exc:
        raise ErreurClient(f"réponse non-JSON: {ligne!r}") from exc
    return reponse


def cmd_search(host: str, port: int, hote: str) -> Domaine | None:
    rep = _envoyer(host, port, {"cmd": "SEARCH", "arg": hote})
    if rep.get("status") == "NOT_FOUND":
        return None
    if rep.get("status") == "OK":
        return Domaine(**rep["domaine"])
    raise ErreurClient(rep.get("message", "erreur inconnue"))


def cmd_record(host: str, port: int, hote: str) -> str:
    rep = _envoyer(host, port, {"cmd": "RECORD", "arg": hote})
    statut = rep.get("status")
    if statut in ("OK", "ALREADY_EXISTS"):
        return statut
    raise ErreurClient(rep.get("message", "échec de l'enregistrement"))


def cmd_count(host: str, port: int) -> int:
    rep = _envoyer(host, port, {"cmd": "COUNT"})
    if rep.get("status") == "OK":
        return int(rep["count"])
    raise ErreurClient(rep.get("message", "erreur COUNT"))


def cmd_list(host: str, port: int) -> list[str]:
    rep = _envoyer(host, port, {"cmd": "LIST"})
    if rep.get("status") == "OK":
        return list(rep["hotes"])
    raise ErreurClient(rep.get("message", "erreur LIST"))


# ============================================================================
# PARTIE 5 — Interface CLI (argparse + logging)
# ============================================================================
def configurer_logging(verbosite: int) -> None:
    """Configure le logging une seule fois selon le nombre de -v.

    0 -> WARNING, 1 (-v) -> INFO, 2 (-vv) -> DEBUG (format simple),
    3+ (-vvv) -> DEBUG avec format détaillé (timestamp, fichier, ligne, thread).
    Tout part sur stderr (la convention : stdout pour les résultats).
    """
    if verbosite >= 3:
        niveau = logging.DEBUG
        fmt = "%(asctime)s %(levelname)s [%(threadName)s] %(filename)s:%(lineno)d — %(message)s"
    elif verbosite == 2:
        niveau = logging.DEBUG
        fmt = "%(levelname)s — %(message)s"
    elif verbosite == 1:
        niveau = logging.INFO
        fmt = "%(levelname)s — %(message)s"
    else:
        niveau = logging.WARNING
        fmt = "%(levelname)s — %(message)s"

    logging.basicConfig(level=niveau, format=fmt, stream=sys.stderr)


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="annuaire.py",
        description="Mini-annuaire de domaines (serveur/client).",
    )
    parseur.add_argument(
        "-v",
        action="count",
        default=0,
        dest="verbosite",
        help="augmente la verbosité (-v INFO, -vv DEBUG, -vvv détaillé)",
    )

    sous = parseur.add_subparsers(dest="commande", required=True)

    sous.add_parser("serve", help="lance le serveur (P3)")

    p_search = sous.add_parser("search", help="envoie SEARCH au serveur")
    p_search.add_argument("hote", help="nom d'hôte à rechercher")

    p_record = sous.add_parser("record", help="envoie RECORD au serveur")
    p_record.add_argument("hote", help="nom d'hôte à collecter et enregistrer")

    sous.add_parser("count", help="envoie COUNT")
    sous.add_parser("list", help="envoie LIST")

    return parseur


def main(argv: list[str] | None = None) -> int:
    parseur = construire_parseur()
    args = parseur.parse_args(argv)

    configurer_logging(args.verbosite)
    charger_env()
    host, port = config_reseau()

    if args.commande == "serve":
        lancer_serveur(host, port)
        return 0

    # Modes client : les erreurs réseau partent sur stderr, le résultat sur stdout.
    try:
        if args.commande == "search":
            dom = cmd_search(host, port, args.hote)
            if dom is None:
                print("NOT_FOUND")
            else:
                print(json.dumps(dom.model_dump(mode="json"), ensure_ascii=False, indent=2))

        elif args.commande == "record":
            statut = cmd_record(host, port, args.hote)
            print(statut)

        elif args.commande == "count":
            print(cmd_count(host, port))

        elif args.commande == "list":
            for hote in cmd_list(host, port):
                print(hote)

    except ErreurClient as exc:
        logger.error("%s", exc)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
