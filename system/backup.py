import sys
import shutil
from pathlib import Path
from datetime import datetime

chemin_source = Path(sys.argv[1])

horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")

nom_backup = f"backup_{horodatage}"
chemin_backup = chemin_source.parent / nom_backup

shutil.copytree(chemin_source, chemin_backup)

nombre_fichiers = sum(1 for f in chemin_backup.rglob("*") if f.is_file())

print(f"Backup créé : {chemin_backup}")
print(f"Fichiers copiés : {nombre_fichiers}")
