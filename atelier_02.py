import socket

socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_unix = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

with socket_tcp, socket_udp, socket_unix:

    print("--- Socket TCP ---")
    print("Numéro (fileno) :", socket_tcp.fileno())
    print("Famille         :", socket_tcp.family.name)
    print("Type            :", socket_tcp.type.name)

    print("--- Socket UDP ---")
    print("Numéro (fileno) :", socket_udp.fileno())
    print("Famille         :", socket_udp.family.name)
    print("Type            :", socket_udp.type.name)

    print("--- Socket Unix ---")
    print("Numéro (fileno) :", socket_unix.fileno())
    print("Famille         :", socket_unix.family.name)
    print("Type            :", socket_unix.type.name)