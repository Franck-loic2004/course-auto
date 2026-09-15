"""
main.py — Point d'entrée en ligne de commande (version simplifiée).

Exemples :
    python main.py init
    python main.py ajouter "Farine"
    python main.py retirer "Farine"
    python main.py liste
    python main.py achete
"""
import sys
from db import init_db
from stock import ajouter_a_liste, retirer_de_liste, get_liste_courses, marquer_liste_comme_achetee


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    commande = sys.argv[1]

    if commande == "init":
        init_db()
        print("✅ Base initialisée.")

    elif commande == "ajouter":
        nom = " ".join(sys.argv[2:])
        ajoute = ajouter_a_liste(nom)
        if ajoute:
            print(f"✅ Ajouté à la liste : {nom}")
        else:
            print(f"ℹ️ {nom} était déjà dans la liste.")

    elif commande == "retirer":
        nom = " ".join(sys.argv[2:])
        if retirer_de_liste(nom):
            print(f"✅ Retiré de la liste : {nom}")
        else:
            print(f"ℹ️ {nom} n'était pas dans la liste.")

    elif commande == "liste":
        liste = get_liste_courses()
        if not liste:
            print("La liste de courses est vide.")
        for nom in liste:
            print(f"- {nom}")

    elif commande == "achete":
        marquer_liste_comme_achetee()
        print("✅ Liste vidée, courses marquées comme faites.")

    else:
        print(f"Commande inconnue : {commande}")
        print(__doc__)


if __name__ == "__main__":
    main()