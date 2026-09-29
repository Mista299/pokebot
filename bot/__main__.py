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

    ctx.user_data["ultimo_pokemon"] = data

    tipos = ", ".join(t["type"]["name"] for t in data["types"])
    texto = (
        f"🔎 *{data['name'].title()}* (#{data['id']})\n"
        f"Tipo: {tipos}\n"
        f"Altura: {data['height']/10} m\n"
        f"Peso: {data['weight']/10} kg"
    )
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats", callback_data="stats"),
         InlineKeyboardButton("🎨 Sprite", callback_data="sprite")],
    ])
    await update.message.reply_text(
        texto,
        reply_markup=teclado,
        parse_mode="Markdown",
    )


async def botones_pokemon(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = ctx.user_data.get("ultimo_pokemon")
    if not data:
        await q.edit_message_text("⚠️ Primero usa /poke")
        return
    accion = q.data
    if accion == "stats":
        stats = "\n".join(
            f"• {s['stat']['name']}: {s['base_stat']}"
            for s in data["stats"]
        )
        await q.edit_message_text(
            f"📊 *Stats de {data['name'].title()}*\n\n{stats}",
            parse_mode="Markdown",
        )
    elif accion == "sprite":
        url = data["sprites"]["front_default"]
        await q.edit_message_text(f"🎨 {url or 'Sin sprite'}")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", hola))
    app.add_handler(CommandHandler("poke", poke))
    app.add_handler(CallbackQueryHandler(botones_pokemon, pattern="^(stats|sprite)$"))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()