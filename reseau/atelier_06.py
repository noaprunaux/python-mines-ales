import socket
import struct

def recv_exactement(sock, nombre_octets):
    """Lit exactement 'nombre_octets' octets sur le socket, sans en lire ni plus ni moins."""
    morceaux = []
    octets_restants = nombre_octets

    while octets_restants > 0:
        morceau = sock.recv(octets_restants)

        if morceau == b"":
            raise RuntimeError("Connexion fermée trop tôt !")

        morceaux.append(morceau)
        octets_restants -= len(morceau)

    return b"".join(morceaux)



def envoyer_message(sock, message: bytes) -> None:
    """Envoie un message précédé de sa longueur encodée sur 4 octets."""

    taille = len(message)

    entete = struct.pack("!I", taille)

    sock.sendall(entete)
    sock.sendall(message)



def recevoir_message(sock) -> bytes:
    """Lit un message en lisant d'abord les 4 octets d'en-tête, puis le contenu."""

    entete = recv_exactement(sock, 4)

    taille = struct.unpack("!I", entete)[0]

    message = recv_exactement(sock, taille)

    return message



def main():
    sock_emetteur, sock_recepteur = socket.socketpair()

    try:
        messages_envoyes = [b"a", b"bb", b"ccc"]

        for msg in messages_envoyes:
            envoyer_message(sock_emetteur, msg)
            print(f"Envoyé    : {msg} ({len(msg)} octet(s))")

        print()

        for msg_original in messages_envoyes:
            msg_recu = recevoir_message(sock_recepteur)
            print(f"Reçu      : {msg_recu} ({len(msg_recu)} octet(s))")

            if msg_recu == msg_original:
                print(f"Identique à l'original")
            else:
                print(f"Différent de l'original !")

            print()

    finally:
        sock_emetteur.close()
        sock_recepteur.close()


if __name__ == "__main__":
    main()