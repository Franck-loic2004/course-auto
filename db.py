"""
db.py — Connexion et initialisation de la base de données SQLite.
Version simplifiée : on ne suit plus de quantités/seuils, juste une liste
de produits "à acheter" ou "déjà achetés".
"""
import os
import sqlite3
from pathlib import Path

# En local : courses.db à côté du script.
# En prod (Railway) : DB_PATH pointe vers le volume persistant monté,
# ex. /data/courses.db, via la variable d'environnement DB_PATH.
DB_PATH = Path(os.environ.get("DB_PATH", Path(__file__).parent / "courses.db"))

# S'assure que le dossier parent existe (utile pour /data sur un volume Railway).
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crée les tables si elles n'existent pas encore."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS produit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            statut TEXT NOT NULL DEFAULT 'a_acheter',
            date_ajout TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS config (
            cle TEXT PRIMARY KEY,
            valeur TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_config(cle: str) -> str | None:
    conn = get_connection()
    row = conn.execute("SELECT valeur FROM config WHERE cle = ?", (cle,)).fetchone()
    conn.close()
    return row["valeur"] if row else None


def set_config(cle: str, valeur: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO config (cle, valeur) VALUES (?, ?) "
        "ON CONFLICT(cle) DO UPDATE SET valeur = ?",
        (cle, valeur, valeur),
    )
    conn.commit()
    conn.close()