import argparse
import sys

def main():
    # 1. Création du parseur
    parser = argparse.ArgumentParser(description="Mini-calculatrice en ligne de commande")

    # 2. Ajout des trois arguments positionnels
    # "type=float" convertit automatiquement le texte tapé en nombre décimal
    parser.add_argument("nombre1", type=float, help="Le premier nombre")
    
    # "choices" restreint l'entrée aux valeurs autorisées. 
    # Si l'utilisateur tape autre chose, argparse générera une erreur automatiquement.
    parser.add_argument("operateur", choices=["+", "-", "*", "/"], help="L'opérateur (+, -, *, /)")
    
    parser.add_argument("nombre2", type=float, help="Le deuxième nombre")

    # 3. Analyse des arguments passés dans le terminal
    args = parser.parse_args()

    # 4. Logique de la calculatrice
    if args.operateur == "+":
        resultat = args.nombre1 + args.nombre2
    elif args.operateur == "-":
        resultat = args.nombre1 - args.nombre2
    elif args.operateur == "*":
        resultat = args.nombre1 * args.nombre2
    elif args.operateur == "/":
        if args.nombre2 == 0:
            # Envoi du message d'erreur sur la sortie standard d'erreur (stderr)
            print("Erreur : division par zéro", file=sys.stderr)
            sys.exit(1) # Code 1 pour signaler au système (shell) que le script a échoué
        resultat = args.nombre1 / args.nombre2

    # 5. Affichage du résultat
    print(f"{args.nombre1} {args.operateur} {args.nombre2} = {resultat}")

if __name__ == "__main__":
    main()
