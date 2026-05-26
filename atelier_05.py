import socket

def recv_ligne(sock):
    """Lit une ligne (terminée par b\"\\n\") sur le socket, et renvoie les octets sans le \\n."""
    morceaux = []

    while True:
        octet = sock.recv(1)

        if octet == b"":
            break

        if octet == b"\n":
            break

        morceaux.append(octet)

    return b"".join(morceaux)


def main():
    sock_emetteur, sock_recepteur = socket.socketpair()

    try:
        message = b"bonjour\nle monde\n"
        sock_emetteur.sendall(message)

        ligne1 = recv_ligne(sock_recepteur)
        ligne2 = recv_ligne(sock_recepteur)

        print("Ligne 1 reçue :", ligne1)
        print("Ligne 2 reçue :", ligne2)

    finally:
        sock_emetteur.close()
        sock_recepteur.close()


if __name__ == "__main__":
    main()

# C'est inefficace car on lit un octet à la fois