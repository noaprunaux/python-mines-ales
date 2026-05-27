import sys
import datetime

message = sys.argv[1]

horodatage = datetime.datetime.now().isoformat(timespec="seconds")

with open("app.log", "a") as fichier:
    fichier.write(f"{horodatage} {message}\n")
