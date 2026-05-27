import struct

octets = b"\x00\x00\x00\x2A"

valeur_big = struct.unpack("!I", octets)[0]

valeur_little = struct.unpack("<I", octets)[0]

octets_inverses = octets[::-1]
valeur_inverse_puis_big = struct.unpack("!I", octets_inverses)[0]

print(f"Octets bruts               : {octets.hex(' ')}")
print(f"1. Big-endian              : {valeur_big}")
print(f"2. Little-endian           : {valeur_little}")
print(f"3. Octets inversés + big   : {valeur_inverse_puis_big}")
print()

if valeur_little == valeur_inverse_puis_big:
    print("Valeurs 2 et 3 sont identiques.")
else:
    print("Valeurs 2 et 3 sont DIFFÉRENTES.")
