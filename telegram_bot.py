"""
telegram_bot.py — Bot Telegram pour signaler qu'un produit manque.

Configuration :
    1. Ouvre Telegram, cherche @BotFather
    2. Envoie /newbot, suis les instructions -> tu reçois un TOKEN
    3. Lance ce script avec : TELEGRAM_BOT_TOKEN=xxxx python telegram_bot.py
    4. Ta mère cherche le bot par son nom et envoie /start

Usage côté utilisateur (dans Telegram) :
    farine                  -> ajoute "farine" à la liste de courses
    /liste                  -> affiche la liste de courses actuelle
    /retirer <nom>          -> enlève un produit ajouté par erreur
    /achete                 -> vide la liste une fois les courses faites
"""
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from db import init_db
from stock import ajouter_a_liste, retirer_de_liste, get_liste_courses, marquer_liste_comme_achetee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salut ! Je gère la liste de courses.\n\n"
        "Pour ajouter un produit manquant, écris juste son nom :\n"
        "  farine\n"
        "  lait\n\n"
        "Commandes utiles :\n"
        "/liste - voir la liste de courses\n"
        "/retirer <nom> - enlever un produit ajouté par erreur\n"
        "/achete - vider la liste une fois les courses faites"
    )


async def liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = get_liste_courses()
    if not items:
        await update.message.reply_text("👍 Rien à acheter pour le moment.")
        return
    texte = "🛒 Liste de courses :\n" + "\n".join(f"- {nom}" for nom in items)
    await update.message.reply_text(texte)


async def retirer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nom = " ".join(context.args)
    if not nom:
        await update.message.reply_text("Format : /retirer <nom du produit>")
        return

    if retirer_de_liste(nom):
        await update.message.reply_text(f"✅ Retiré de la liste : {nom}")
    else:
        await update.message.reply_text(f"ℹ️ {nom} n'était pas dans la liste.")


async def achete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    marquer_liste_comme_achetee()
    await update.message.reply_text("✅ Liste vidée, bonnes courses !")


async def gerer_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tout message texte qui n'est pas une commande = un produit à ajouter."""
    nom = update.message.text.strip()

    if not nom:
        return

    ajoute = ajouter_a_liste(nom)
    if ajoute:
        await update.message.reply_text(f"✅ Ajouté à la liste : {nom}")
    else:
        await update.message.reply_text(f"ℹ️ {nom} était déjà dans la liste.")


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
    app.add_handler(CommandHandler("retirer", retirer))
    app.add_handler(CommandHandler("achete", achete))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerer_message))

    logger.info("Bot démarré, en écoute...")
    app.run_polling()


if __name__ == "__main__":
    main()