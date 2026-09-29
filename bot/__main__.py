from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ContextTypes,
)
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise RuntimeError("Falta TELEGRAM_TOKEN en el .env")

from bot.api_client import APIError, PAGE_SIZE, get_pokemon, listar_pokemones


async def hola(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola mundo 👋")


async def poke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Uso: /poke <nombre_o_id>")
        return
    nombre = ctx.args[0]
    try:
        data = await get_pokemon(nombre)
    except APIError as e:
        await update.message.reply_text(f"❌ {e}")
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


def _render_lista(data: dict) -> tuple[str, InlineKeyboardMarkup]:
    """Arma el mensaje + teclado para una pagina de resultados."""
    nombres = [p["name"] for p in data["results"]]
    if data["next"]:
        offset_actual = int(data["next"].split("offset=")[1].split("&")[0]) - PAGE_SIZE
    else:
        offset_actual = data["count"] - len(nombres)
    inicio = offset_actual + 1
    fin = offset_actual + len(nombres)
    total = data["count"]

    texto = (
        f"📜 *Pokémons {inicio}–{fin} de {total}*\n"
        f"_Copiá uno y usá:_ `/poke nombre`\n\n"
    )
    nombres_fmt = [f"`{n}`" for n in nombres]
    filas_texto = []
    for i in range(0, len(nombres_fmt), 2):
        fila = nombres_fmt[i:i+2]
        filas_texto.append("  ".join(fila))
    texto += "\n".join(filas_texto)

    botones = []
    if data["previous"]:
        prev_offset = max(0, offset_actual - PAGE_SIZE)
        botones.append(InlineKeyboardButton(
            "« Anterior", callback_data=f"lista:{prev_offset}"
        ))
    botones.append(InlineKeyboardButton(
        f"{fin}/{total}", callback_data="noop"
    ))
    if data["next"]:
        next_offset = offset_actual + PAGE_SIZE
        botones.append(InlineKeyboardButton(
            "Siguiente »", callback_data=f"lista:{next_offset}"
        ))
    teclado = InlineKeyboardMarkup([botones])
    return texto, teclado


async def pokemones(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Lista paginada de nombres de pokemons."""
    offset = 0
    if ctx.args and ctx.args[0].isdigit():
        offset = int(ctx.args[0])
    try:
        data = await listar_pokemones(offset=offset)
    except APIError as e:
        await update.message.reply_text(f"❌ {e}")
        return
    texto, teclado = _render_lista(data)
    await update.message.reply_text(texto, reply_markup=teclado, parse_mode="Markdown")


async def callback_lista(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "noop":
        return
    if not q.data.startswith("lista:"):
        return
    offset = int(q.data.split(":", 1)[1])
    try:
        data = await listar_pokemones(offset=offset)
    except APIError as e:
        await q.edit_message_text(f"❌ {e}")
        return
    texto, teclado = _render_lista(data)
    await q.edit_message_text(texto, reply_markup=teclado, parse_mode="Markdown")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", hola))
    app.add_handler(CommandHandler("poke", poke))
    app.add_handler(CommandHandler("pokemones", pokemones))
    app.add_handler(CallbackQueryHandler(
        botones_pokemon, pattern="^(stats|sprite)$"
    ))
    app.add_handler(CallbackQueryHandler(callback_lista, pattern=r"^(lista:|noop)"))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()