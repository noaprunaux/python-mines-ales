import tarfile
import tempfile
from pathlib import Path


$dossier_temporaire = Path(tempfile.mkdtemp())

fichier1 = dossier_temporaire / "notes.txt"
fichier2 = dossier_temporaire / "config.cfg"
fichier3 = dossier_temporaire / "rapport.md"

fichier1.write_text("Contenu du fichier 1\n")
fichier2.write_text("param=valeur\n")
fichier3.write_text("# Mon rapport\nVoici le contenu.\n")

print(f"Dossier source créé : {dossier_temporaire}")

chemin_archive = dossier_temporaire / "archive.tar.gz"

with tarfile.open(chemin_archive, "w:gz") as tar:
    tar.add(fichier1, arcname=fichier1.name)
    tar.add(fichier2, arcname=fichier2.name)
    tar.add(fichier3, arcname=fichier3.name)

print(f"Archive créée     : {chemin_archive}")

dossier_cible = Path("cible")
dossier_cible.mkdir(exist_ok=True)

with tarfile.open(chemin_archive, "r:gz") as tar:
    tar.extractall(dossier_cible, filter="data")

print(f"Extraction dans   : {dossier_cible.resolve()}")

fichiers_extraits = [f for f in dossier_cible.rglob("*") if f.is_file()]

print(f"\nFichiers extraits ({len(fichiers_extraits)}) :")
for fichier in fichiers_extraits:
    print(f"  {fichier}")
