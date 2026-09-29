from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise RuntimeError("Falta TELEGRAM_TOKEN en el .env")


async def hola(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola mundo 👋")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", hola))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()