"""
stock.py — Logique métier : gestion du stock et de la liste de courses.
"""
from db import get_connection


# ---------- Gestion des ingrédients ----------

def ajouter_ingredient(nom: str, quantite_actuelle: float, unite: str,
                        seuil_min: float, quantite_a_racheter: float = 1) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT OR IGNORE INTO ingredient
           (nom, quantite_actuelle, unite, seuil_min, quantite_a_racheter)
           VALUES (?, ?, ?, ?, ?)""",
        (nom, quantite_actuelle, unite, seuil_min, quantite_a_racheter),
    )
    conn.commit()
    conn.close()


def get_all_ingredients():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM ingredient").fetchall()
    conn.close()
    return rows


# ---------- Consommation (= tu utilises un ingrédient) ----------

def consommer_ingredient(nom: str, quantite: float) -> None:
    """Décrémente le stock et enregistre l'événement dans l'historique."""
    conn = get_connection()
    ing = conn.execute("SELECT * FROM ingredient WHERE nom = ?", (nom,)).fetchone()

    if ing is None:
        print(f"⚠️  Ingrédient inconnu : {nom}")
        conn.close()
        return

    nouvelle_quantite = max(0, ing["quantite_actuelle"] - quantite)
    conn.execute(
        "UPDATE ingredient SET quantite_actuelle = ? WHERE id = ?",
        (nouvelle_quantite, ing["id"]),
    )
    conn.execute(
        """INSERT INTO historique_consommation (ingredient_id, quantite_utilisee)
           VALUES (?, ?)""",
        (ing["id"], quantite),
    )
    conn.commit()
    conn.close()

    print(f"✅ {nom} : {ing['quantite_actuelle']} → {nouvelle_quantite} {ing['unite']}")


# ---------- Vérification du stock + génération de la liste de courses ----------

def verifier_stock() -> list[str]:
    """
    Parcourt tous les ingrédients. Si un ingrédient est sous son seuil_min
    et n'est pas déjà dans la liste (statut 'a_acheter'), on l'ajoute.
    Retourne la liste des noms ajoutés.
    """
    conn = get_connection()
    ingredients = conn.execute("SELECT * FROM ingredient").fetchall()

    ajoutes = []
    for ing in ingredients:
        if ing["quantite_actuelle"] <= ing["seuil_min"]:
            deja_present = conn.execute(
                """SELECT 1 FROM liste_courses
                   WHERE ingredient_id = ? AND statut = 'a_acheter'""",
                (ing["id"],),
            ).fetchone()

            if not deja_present:
                conn.execute(
                    "INSERT INTO liste_courses (ingredient_id) VALUES (?)",
                    (ing["id"],),
                )
                ajoutes.append(ing["nom"])

    conn.commit()
    conn.close()
    return ajoutes


def get_liste_courses() -> list[dict]:
    """Retourne la liste de courses actuelle (statut = a_acheter)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.nom, i.quantite_a_racheter, i.unite
        FROM liste_courses lc
        JOIN ingredient i ON i.id = lc.ingredient_id
        WHERE lc.statut = 'a_acheter'
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def marquer_liste_comme_achetee() -> None:
    """À appeler une fois les courses faites : on vide la liste et on
    remet le stock des ingrédients rachetés à leur quantité cible."""
    conn = get_connection()
    conn.execute("""
        UPDATE ingredient
        SET quantite_actuelle = quantite_a_racheter
        WHERE id IN (
            SELECT ingredient_id FROM liste_courses WHERE statut = 'a_acheter'
        )
    """)
    conn.execute("UPDATE liste_courses SET statut = 'achete' WHERE statut = 'a_acheter'")
    conn.commit()
    conn.close()
