"""
stock.py — Logique métier simplifiée : ajouter/retirer un produit de la
liste de courses, sans gestion de quantité ni de seuil.
"""
from db import get_connection


def ajouter_a_liste(nom: str) -> bool:
    """
    Ajoute un produit à la liste de courses.
    Retourne True si ajouté, False s'il y était déjà.
    """
    nom = nom.strip().capitalize()
    conn = get_connection()

    existe = conn.execute(
        "SELECT 1 FROM produit WHERE nom = ? AND statut = 'a_acheter'", (nom,)
    ).fetchone()

    if existe:
        conn.close()
        return False

    # Upsert : si le produit existe déjà (acheté précédemment), on le
    # repasse en "a_acheter" ; sinon on le crée.
    conn.execute("""
        INSERT INTO produit (nom, statut) VALUES (?, 'a_acheter')
        ON CONFLICT(nom) DO UPDATE SET statut = 'a_acheter'
    """, (nom,))
    conn.commit()
    conn.close()
    return True


def retirer_de_liste(nom: str) -> bool:
    """Retire un produit de la liste (ex: ajouté par erreur)."""
    nom = nom.strip().capitalize()
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM produit WHERE nom = ? AND statut = 'a_acheter'", (nom,)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def get_liste_courses() -> list[str]:
    """Retourne la liste des produits à acheter."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT nom FROM produit WHERE statut = 'a_acheter' ORDER BY date_ajout"
    ).fetchall()
    conn.close()
    return [r["nom"] for r in rows]


def marquer_liste_comme_achetee() -> None:
    """Vide la liste une fois les courses faites."""
    conn = get_connection()
    conn.execute("UPDATE produit SET statut = 'achete' WHERE statut = 'a_acheter'")
    conn.commit()
    conn.close()