"""
db.py — Connexion et initialisation de la base de données SQLite.
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
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            quantite_actuelle REAL NOT NULL DEFAULT 0,
            unite TEXT NOT NULL DEFAULT 'unité',
            seuil_min REAL NOT NULL DEFAULT 0,
            quantite_a_racheter REAL NOT NULL DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS liste_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER NOT NULL,
            date_ajout TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            statut TEXT NOT NULL DEFAULT 'a_acheter',
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(id)
        )
    """)

    # Table d'historique -> utile pour la partie "analytique" plus tard
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historique_consommation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER NOT NULL,
            quantite_utilisee REAL NOT NULL,
            date_evenement TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(id)
        )
    """)

    conn.commit()
    conn.close()