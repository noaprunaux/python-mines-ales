import socket
import argparse


lecteur = argparse.ArgumentParser(description="Tester TCP ou UDP sur 127.0.0.1:1")

lecteur.add_argument("--protocole", choices=["tcp", "udp"], required=True,)
args = lecteur.parse_args()

if args.protocole == "tcp":

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    socket.settimeout(1)

    try:
        socket.connect(("127.0.0.1", 1))

    except ConnectionRefusedError:
        print("TCP → connexion refusée")

    finally:
        socket.close()

elif args.protocole == "udp":

    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = "test".encode()

    octets_envoyes = socket.sendto(message, ("127.0.0.1", 1))

    print(f"UDP → datagramme envoyé ({octets_envoyes} octet(s)), aucune confirmation possible")

    socket.close()