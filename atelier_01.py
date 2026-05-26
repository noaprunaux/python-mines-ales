import sys
import socket

nom = sys.argv[1]

enregistrements = socket.getaddrinfo(nom, None)

ipv4 = []
ipv6 = []

for info in enregistrements:
    famille = info[0]
    adresse = info[4][0]
    
    if famille == socket.AF_INET and adresse not in ipv4:
        ipv4.append(adresse)
        
    elif famille == socket.AF_INET6 and adresse not in ipv6:
        ipv6.append(adresse)

for ip in ipv4:
    print(f"IPv4 : {ip}")

for ip in ipv6:
    print(f"IPv6 : {ip}")

total = len(ipv4) + len(ipv6)
print(f"Total : {total} enregistrement(s)")