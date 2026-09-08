"""
telegram_bot.py — Bot Telegram pour signaler la consommation d'ingrédients
et consulter la liste de courses, sans passer par la ligne de commande.

Configuration :
    1. Ouvre Telegram, cherche @BotFather
    2. Envoie /newbot, suis les instructions -> tu reçois un TOKEN
    3. Lance ce script avec : TELEGRAM_BOT_TOKEN=xxxx python telegram_bot.py
    4. Ta mère cherche le bot par son nom et envoie /start

Usage côté utilisateur (dans Telegram) :
    /start                  -> message d'accueil + liste des commandes
    /liste                  -> affiche la liste de courses actuelle
    /verifier                -> relance la vérification du stock
    farine 300               -> signale qu'on a utilisé 300 (unité par défaut) de farine
    lait 1                   -> idem pour le lait
"""
import logging
import os
import re

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from db import init_db, get_connection
from stock import consommer_ingredient, verifier_stock, get_liste_courses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Regex simple : "farine 300" / "Farine  300" / "lait 1.5"
PATTERN_CONSOMMATION = re.compile(r"^([a-zA-ZÀ-ÿ\- ]+?)\s+(\d+(?:[.,]\d+)?)\s*$")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salut la famille Megam! Je gère la liste de courses de la famille.\n\n"
        "Pour signaler qu'un ingrédient a été utilisé, écris simplement :\n"
        "  farine 300\n"
        "  lait 1\n\n"
        "Commandes utiles :\n"
        "/liste - voir la liste de courses\n"
        "/verifier - forcer une vérification du stock\n"
        "/stock - voir tout le stock actuel"
    )


async def liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = get_liste_courses()
    if not items:
        await update.message.reply_text("👍 Rien à acheter pour le moment.")
        return
    texte = "🛒 Liste de courses :\n" + "\n".join(
        f"- {i['nom']} ({i['quantite_a_racheter']} {i['unite']})" for i in items
    )
    await update.message.reply_text(texte)


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    rows = conn.execute("SELECT nom, quantite_actuelle, unite FROM ingredient").fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Aucun ingrédient enregistré encore.")
        return
    texte = "📦 Stock actuel :\n" + "\n".join(
        f"- {r['nom']} : {r['quantite_actuelle']} {r['unite']}" for r in rows
    )
    await update.message.reply_text(texte)


async def verifier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ajoutes = verifier_stock()
    if ajoutes:
        await update.message.reply_text("🛒 Ajouté(s) à la liste : " + ", ".join(ajoutes))
    else:
        await update.message.reply_text("👍 Rien de nouveau, le stock est suffisant.")


async def gerer_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Intercepte les messages du type 'farine 300' pour décrémenter le stock."""
    texte = update.message.text.strip().lower()
    match = PATTERN_CONSOMMATION.match(texte)

    if not match:
        await update.message.reply_text(
            "Je n'ai pas compris 🤔 Écris par exemple : farine 300"
        )
        return

    nom, quantite_str = match.groups()
    quantite = float(quantite_str.replace(",", "."))
    nom = nom.strip().capitalize()

    conn = get_connection()
    existe = conn.execute("SELECT 1 FROM ingredient WHERE nom = ?", (nom,)).fetchone()
    conn.close()

    if not existe:
        await update.message.reply_text(f"⚠️ Je ne connais pas '{nom}'. Demande à Franck de l'ajouter.")
        return

    consommer_ingredient(nom, quantite)
    ajoutes = verifier_stock()

    reponse = f"✅ Noté : {nom} -{quantite}"
    if nom in ajoutes:
        reponse += f"\n🛒 {nom} est maintenant sur la liste de courses !"
    await update.message.reply_text(reponse)


def main():
    if not TOKEN:
        raise RuntimeError(
            "⚠️ Variable d'environnement TELEGRAM_BOT_TOKEN manquante. "
            "Lance avec : TELEGRAM_BOT_TOKEN=xxxx python telegram_bot.py"
        )

    init_db()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("liste", liste))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("verifier", verifier))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerer_message))

    logger.info("Bot démarré, en écoute...")
    app.run_polling()


if __name__ == "__main__":
    main()