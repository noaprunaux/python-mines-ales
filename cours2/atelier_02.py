from datetime import datetime
date = datetime.now().year

prénom = input("Quel est ton prénom ? ")
age = input("Quel est ton âge ? ")
annee = date - int(age)

print(f"Bonjour, {prénom}, tu as {age} ans, donc tu es né(e) vers {annee}.")
