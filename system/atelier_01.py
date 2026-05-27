import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Mini-calculatrice en ligne de commande")

    parser.add_argument("nombre1", type=float, help="Le premier nombre")
    
    parser.add_argument("operateur", choices=["+", "-", "*", "/"], help="L'opérateur (+, -, *, /)")
    
    parser.add_argument("nombre2", type=float, help="Le deuxième nombre")

    args = parser.parse_args()

    if args.operateur == "+":
        resultat = args.nombre1 + args.nombre2
    elif args.operateur == "-":
        resultat = args.nombre1 - args.nombre2
    elif args.operateur == "*":
        resultat = args.nombre1 * args.nombre2
    elif args.operateur == "/":
        if args.nombre2 == 0:
            print("Erreur : division par zéro", file=sys.stderr)
            sys.exit(1)
        resultat = args.nombre1 / args.nombre2

    print(f"{args.nombre1} {args.operateur} {args.nombre2} = {resultat}")

if __name__ == "__main__":
    main()
