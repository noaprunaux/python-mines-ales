"""Tests de la couche données (CRUD) en isolation — bonus.

On reconstruit un engine/Session sur une base SQLite temporaire et on
monkeypatche les symboles du module ``annuaire`` afin de ne dépendre ni du
réseau ni de la collecte système (nslookup/whois).
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import annuaire


@pytest.fixture()
def bdd_temporaire(tmp_path, monkeypatch):
    """Branche le module sur une base SQLite jetable, vide à chaque test."""
    chemin = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{chemin}",
        connect_args={"check_same_thread": False},
    )
    SessionTest = sessionmaker(bind=engine)
    monkeypatch.setattr(annuaire, "engine", engine)
    monkeypatch.setattr(annuaire, "Session", SessionTest)
    annuaire.Base.metadata.create_all(engine)
    yield
    annuaire.Base.metadata.drop_all(engine)


def _domaine(hote="example.com"):
    return annuaire.Domaine(
        hote=hote,
        ip="93.184.216.34",
        contact="Jane Doe",
        email="admin@example.com",
    )


def test_enregistrer_et_chercher(bdd_temporaire):
    annuaire.enregistrer(_domaine())
    trouve = annuaire.chercher("example.com")
    assert trouve is not None
    assert trouve.hote == "example.com"
    assert trouve.ip == "93.184.216.34"
    assert trouve.contact == "Jane Doe"
    assert str(trouve.email) == "admin@example.com"


def test_chercher_absent_renvoie_none(bdd_temporaire):
    assert annuaire.chercher("inconnu.test") is None


def test_enregistrer_doublon_leve_value_error(bdd_temporaire):
    annuaire.enregistrer(_domaine())
    with pytest.raises(ValueError):
        annuaire.enregistrer(_domaine())


def test_lister_et_compter(bdd_temporaire):
    assert annuaire.compter() == 0
    assert annuaire.lister() == []
    annuaire.enregistrer(_domaine("a.com"))
    annuaire.enregistrer(_domaine("b.com"))
    assert annuaire.compter() == 2
    hotes = sorted(d.hote for d in annuaire.lister())
    assert hotes == ["a.com", "b.com"]


def test_champs_optionnels_none(bdd_temporaire):
    dom = annuaire.Domaine(hote="vide.test")
    annuaire.enregistrer(dom)
    trouve = annuaire.chercher("vide.test")
    assert trouve is not None
    assert trouve.ip is None
    assert trouve.contact is None
    assert trouve.email is None
