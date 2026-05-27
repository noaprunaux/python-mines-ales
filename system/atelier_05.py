import argparse

def main():
    parser = argparse.ArgumentParser(description="Convertisseur de température")

    parser.add_argument("valeur", type=float)

    parser.add_argument(
        "--from",
        dest="depuis",
        required=True,
        choices=["celsius", "fahrenheit", "kelvin"],
    )

    parser.add_argument(
        "--to",
        dest="vers",
        required=True,
        choices=["celsius", "fahrenheit", "kelvin"],
    )

    parser.add_argument(
        "--precision",
        type=int,
        default=2,
    )

    args = parser.parse_args()

    if args.depuis == args.vers:
        resultat = args.valeur
    else:
        if args.depuis == "celsius":
            en_celsius = args.valeur
        elif args.depuis == "fahrenheit":
            en_celsius = (args.valeur - 32) * 5 / 9
        elif args.depuis == "kelvin":
            en_celsius = args.valeur - 273.15

        if args.vers == "celsius":
            resultat = en_celsius
        elif args.vers == "fahrenheit":
            resultat = en_celsius * 9 / 5 + 32
        elif args.vers == "kelvin":
            resultat = en_celsius + 273.15

    valeur_formatee = f"{args.valeur:.{args.precision}f}"
    resultat_formate = f"{resultat:.{args.precision}f}"

    print(f"{valeur_formatee} {args.depuis} = {resultat_formate} {args.vers}")


if __name__ == "__main__":
    main()
