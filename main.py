"""
main.py — Point d'entrée en ligne de commande.

Exemples :
    python main.py init
    python main.py ajouter "Farine" 1000 g 200 1000
    python main.py consommer "Farine" 300
    python main.py verifier
    python main.py liste
    python main.py achete
"""
import sys
from db import init_db
from stock import (
    ajouter_ingredient,
    consommer_ingredient,
    verifier_stock,
    get_liste_courses,
    marquer_liste_comme_achetee,
)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    commande = sys.argv[1]

    if commande == "init":
        init_db()
        print("✅ Base initialisée.")

    elif commande == "ajouter":
        # ajouter "Farine" 1000 g 200 1000
        nom, quantite, unite, seuil, a_racheter = sys.argv[2:7]
        ajouter_ingredient(nom, float(quantite), unite, float(seuil), float(a_racheter))
        print(f"✅ Ingrédient ajouté : {nom}")

    elif commande == "consommer":
        nom, quantite = sys.argv[2], float(sys.argv[3])
        consommer_ingredient(nom, quantite)

    elif commande == "verifier":
        ajoutes = verifier_stock()
        if ajoutes:
            print("🛒 Ajoutés à la liste de courses :", ", ".join(ajoutes))
        else:
            print("👍 Rien à ajouter, le stock est suffisant.")

    elif commande == "liste":
        liste = get_liste_courses()
        if not liste:
            print("La liste de courses est vide.")
        for item in liste:
            print(f"- {item['nom']} ({item['quantite_a_racheter']} {item['unite']})")

    elif commande == "achete":
        marquer_liste_comme_achetee()
        print("✅ Liste marquée comme achetée, stock remis à jour.")

    else:
        print(f"Commande inconnue : {commande}")
        print(__doc__)


if __name__ == "__main__":
    main()
