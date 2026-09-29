from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise RuntimeError("Falta TELEGRAM_TOKEN en el .env")

from bot.api_client import get_pokemon


async def hola(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola mundo 👋")


async def poke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Uso: /poke <nombre_o_id>")
        return
    nombre = ctx.args[0]
    try:
        data = await get_pokemon(nombre)
    except httpx.HTTPStatusError:
        await update.message.reply_text(f"❌ No encontré '{nombre}'")
        return
    await update.message.reply_text(f"Encontré: {data['name']}")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", hola))
    app.add_handler(CommandHandler("poke", poke))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()