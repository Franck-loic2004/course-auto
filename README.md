# Courses Auto

Petit projet d'automatisation : suit le stock d'ingrédients à la maison et
génère automatiquement la liste de courses quand un ingrédient tombe sous
un seuil défini.

## Utilisation

```bash
python main.py init                                   # crée la base
python main.py ajouter "Farine" 1000 g 200 1000        # nom, stock, unité, seuil, quantité à racheter
python main.py consommer "Farine" 300                  # tu utilises 300g
python main.py verifier                                # vérifie le stock, alimente la liste
python main.py liste                                   # affiche la liste de courses
python main.py achete                                  # une fois les courses faites
```

## Modèle de données

- `ingredient` : stock actuel, seuil minimum, quantité à racheter
- `liste_courses` : ce qu'il faut acheter, avec statut
- `historique_consommation` : chaque décrémentation est loguée → base pour
  des stats de consommation plus tard (dashboard, tendances par mois...)

## Bot Telegram (pour que maman signale la consommation)

1. Sur Telegram, cherche **@BotFather**, envoie `/newbot`, choisis un nom
   -> tu reçois un **token**.
2. Installe la dépendance : `pip install python-telegram-bot`
3. Lance le bot :
   ```bash
   TELEGRAM_BOT_TOKEN=xxxxxxxx python telegram_bot.py
   ```
4. Ta mère cherche le bot par son nom sur Telegram et envoie `/start`.
5. Pour signaler une consommation, elle écrit juste : `farine 300` ou
   `lait 1`. Le bot décrémente le stock et l'ajoute à la liste de courses
   automatiquement si besoin.
6. Commandes utiles : `/liste`, `/stock`, `/verifier`

Pour que ça tourne en continu (pas juste quand ton PC est allumé), il
faudra héberger `telegram_bot.py` quelque part (un petit VPS, un Raspberry
Pi à la maison, ou un service gratuit comme Railway/Render).

## Prochaines étapes possibles

1. **Recettes** : associer des ingrédients à une recette, et décrémenter
   automatiquement tout le stock quand on dit "j'ai fait des lasagnes".
2. **Notification automatique** : envoyer la liste par email (`smtplib`) ou
   WhatsApp quand `verifier_stock()` trouve du nouveau.
3. **Automatisation planifiée** : lancer `verifier` chaque jour via `cron`
   (Linux/Mac) ou le Planificateur de tâches (Windows).
4. **Dashboard analytique** : un petit Streamlit qui lit
   `historique_consommation` pour montrer les tendances de consommation —
   c'est la partie qui transforme le projet en "pipeline data" plutôt
   qu'un simple script, intéressant à mettre en avant côté portfolio.
5. **Interface web** : remplacer le CLI par une petite interface React +
   API Node/Express ou Flask si tu veux montrer du full-stack.
