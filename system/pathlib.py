from pathlib import Path


def decomposer(chemin: str) -> tuple:
    p = Path(chemin)

    dossier = str(p.parent)
    nom_sans_extension = p.stem
    extension = p.suffix

    return (dossier, nom_sans_extension, extension)


exemples = [
    "/tmp/a.txt",
    "/var/log/archive.tar.gz",
    "/etc/hosts",
    "/home/noa/documents/rapport.final.pdf",
]

for chemin in exemples:
    resultat = decomposer(chemin)
    print(f"{chemin:<35} -> {resultat}")
