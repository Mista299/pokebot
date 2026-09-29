"""Bot de Telegram - Hola Mundo (v0).

Punto de partida pedagogico. Evolucionar commit por commit siguiendo
el plan en `plan_pedagogico_bot.md` (carpeta padre).
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN_PLACEHOLDER = "PEGA_AQUI_TU_TOKEN_DE_BOTFATHER"


async def hola(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hola mundo 👋")


def main() -> None:
    app = Application.builder().token(TOKEN_PLACEHOLDER).build()
    app.add_handler(CommandHandler("start", hola))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()