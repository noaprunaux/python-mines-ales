import socket


sock1, sock2 = socket.socketpair()

try:
    print(f"fileno()      : {sock1.fileno()}")
    print(f"getsockname() : '{sock1.getsockname()}' (Adresse locale)")
    print(f"getpeername() : '{sock1.getpeername()}' (Adresse du correspondant)")

    print(f"fileno()      : {sock2.fileno()}")
    print(f"getsockname() : '{sock2.getsockname()}' (Adresse locale)")
    print(f"getpeername() : '{sock2.getpeername()}' (Adresse du correspondant)")
    

finally: 
    sock1.close()
    sock2.close()   

# Pourquoi les adresses sont-elles vides ('') ?
# Car socketpair() crée une paire de sockets connectés entre eux, mais sans utiliser le réseau.
# Ils communiquent directement via des canaux de communication internes, sans passer par une adresse IP ou un port. C'est pourquoi les adresses sont vides ('') et ne contiennent
