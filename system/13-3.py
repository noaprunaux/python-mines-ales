import secrets
import tempfile
import os

token = secrets.token_urlsafe(32)

with tempfile.TemporaryDirectory() as tmpdir:
    env_path = os.path.join(tmpdir, ".env")

    with open(env_path, "w") as f:
        f.write(f"TOKEN={token}\n")

    print(f"fichier .env  : {env_path}")
    print(f"contenu       : TOKEN={token[:3]}...")

    with open(env_path, "r") as f:
        for ligne in f:
            cle, _, valeur = ligne.strip().partition("=")
            if cle == "TOKEN":
                token_lu = valeur

    print(f"lu            : {token_lu[:3]}...")

    identique = secrets.compare_digest(token, token_lu)
    print(f"identique     : {identique}")
