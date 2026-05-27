import subprocess
import time

try:
    t0 = time.perf_counter()

    resultat = subprocess.run(
        ["git", "status"],
        capture_output=True,
        check=True
    )

    t1 = time.perf_counter()

    duree_ms = (t1 - t0) * 1000

    print(f"git status terminé en {duree_ms:.1f} ms (code retour {resultat.returncode})")

except FileNotFoundError:
    print("Erreur : git n'est pas installé ou introuvable dans le PATH.")

except subprocess.CalledProcessError as erreur:
    print(f"Erreur : on n'est pas dans un dépôt git (code retour {erreur.returncode}).")
