from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ContextTypes,
)
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

    tipos = ", ".join(t["type"]["name"] for t in data["types"])
    texto = (
        f"🔎 *{data['name'].title()}* (#{data['id']})\n"
        f"Tipo: {tipos}\n"
        f"Altura: {data['height']/10} m\n"
        f"Peso: {data['weight']/10} kg"
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Ver stats", callback_data="stats")],
    ])
    await update.message.reply_text(
        texto,
        reply_markup=teclado,
        parse_mode="Markdown",
    )


async def boton_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("📊 (Acá mostraremos los stats...)")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", hola))
    app.add_handler(CommandHandler("poke", poke))
    app.add_handler(CallbackQueryHandler(boton_stats, pattern="^stats$"))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()