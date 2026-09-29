# Plan pedagógico: de Hola Mundo a un Bot con API pública

Documento de apoyo para la exposición en clase. La idea es **tomar un
bot "hola mundo"** que previamente habrá entregado una compañera y,
sobre ese mismo repositorio, **ir evolucionándolo commit por commit**
mostrando en vivo los cambios y los conceptos nuevos que se agregan.

API elegida para la demo: **[PokeAPI](https://pokeapi.co)**
- Sin API key, sin registro.
- Endpoint base: `https://pokeapi.co/api/v2`.
- Devuelve JSON rico en datos de cada pokémon (tipos, stats, sprites).

Toda la demo usa **una sola API** ([PokeAPI](https://pokeapi.co)) para
mantener coherencia: misma URL base, mismo cliente HTTP, mismo flujo.
No se mezcla con servicios fake.

---

## Índice

1. [Material previo a la clase](#material-previo-a-la-clase)
2. [v0 — Punto de partida (Hola Mundo)](#v0--punto-de-partida-hola-mundo)
3. [v1 — Configuración con `.env`](#v1--configuración-con-env)
4. [v2 — Cliente HTTP con `httpx`](#v2--cliente-http-con-httpx)
5. [v3 — Primer comando que consulta la API](#v3--primer-comando-que-consulta-la-api)
6. [v4 — Formatear la respuesta](#v4--formatear-la-respuesta)
7. [v5 — Inline keyboard (botones)](#v5--inline-keyboard-botones)
8. [v6 — Botones que llaman distintos endpoints](#v6--botones-que-llaman-distintos-endpoints)
9. [v7 — Manejo robusto de errores](#v7--manejo-robusto-de-errores)
10. [v8 — Lista paginada (`/pokemones`)](#v8--lista-paginada-pokemones)
11. [Cierre y preguntas frecuentes](#cierre-y-preguntas-frecuentes)
12. [Cronograma sugerido](#cronograma-sugerido)

---

## Material previo a la clase

### Estructura inicial esperada del repo

```
hola-bot/
├── .env                (no se sube, está en .gitignore)
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── bot/
    ├── __init__.py
    └── __main__.py
```

> Si la estructura real es ligeramente distinta, **adaptar los
> diffs**. El orden pedagógico se mantiene igual.

### `.gitignore` sugerido

```gitignore
.env
__pycache__/
*.pyc
.venv/
```

### `requirements.txt` esperado (puede estar vacío al inicio)

```
python-telegram-bot>=21.0
```

Iremos agregando dependencias **en los commits que las introducen**
(esto es parte del aprendizaje).

---

## v0 — Punto de partida (Hola Mundo)

### Qué hace el bot

Responde `Hola mundo 👋` cuando el usuario envía `/start`.

### Código típico

`bot/__main__.py`:

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


async def hola(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola mundo 👋")


def main():
    app = Application.builder().token("PEGA_AQUI_TU_TOKEN").build()
    app.add_handler(CommandHandler("start", hola))
    app.run_polling()


if __name__ == "__main__":
    main()
```

### Narrativa en clase

> "Este bot solo sabe una cosa: si le escribes `/start`, te saluda.
> No consulta nada en internet, no tiene memoria, no hace nada
> interesante. Vamos a **convertirlo en algo útil** paso a paso."

**Demuestra**: enviar `/start`, ver la respuesta.

---

## v1 — Configuración con `.env`

### Concepto

Los **secretos** (como el token del bot) **no deben estar en el
código**. Si subes el token a GitHub, cualquiera puede tomar el control
de tu bot.

### Cambios

1. Crear `.env.example` en la raíz (sí se sube al repo):

   ```env
   TELEGRAM_TOKEN=
   POKEAPI_BASE=https://pokeapi.co/api/v2
   ```

2. Confirmar que `.env` está en `.gitignore`.

3. Cada desarrollador crea su propio `.env`:

   ```env
   TELEGRAM_TOKEN=123456789:ABCDef...
   POKEAPI_BASE=https://pokeapi.co/api/v2
   ```

4. Modificar `bot/__main__.py`:

```diff
  from telegram import Update
  from telegram.ext import Application, CommandHandler, ContextTypes
+ import os
+ from dotenv import load_dotenv
+
+ load_dotenv()
+ TOKEN = os.getenv("TELEGRAM_TOKEN")
+
+ if not TOKEN:
+     raise RuntimeError("Falta TELEGRAM_TOKEN en el .env")


  async def hola(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      await update.message.reply_text("Hola mundo 👋")


  def main():
-     app = Application.builder().token("PEGA_AQUI_TU_TOKEN").build()
+     app = Application.builder().token(TOKEN).build()
      app.add_handler(CommandHandler("start", hola))
      app.run_polling()
```

5. `requirements.txt`:

```diff
  python-telegram-bot>=21.0
+ python-dotenv>=1.0.1
```

6. `README.md` (añadir una sección):

```markdown
## Configuración
1. Crea un bot en @BotFather y obtén el token.
2. Copia `.env.example` a `.env` y rellena `TELEGRAM_TOKEN`.
3. `pip install -r requirements.txt`
4. `python -m bot`
```

### Commit sugerido

```bash
git add .
git commit -m "v1: leer token desde .env en vez de hardcoded"
```

### Narrativa en clase

> "Si subo este código a GitHub tal cual está, con el token pegado,
> **cualquiera puede usar mi bot** (o hacer cosas peores). Por eso
> movemos el token a una variable de entorno. La librería
> `python-dotenv` lo lee desde un archivo `.env` que **no se sube al
> repositorio**."

**Demuestra**: `git log`, mostrar el diff, mostrar el `.gitignore`.

---

## v2 — Cliente HTTP con `httpx`

### Concepto

Hasta ahora el bot solo lee strings fijos. Para "preguntarle algo a
otra página" necesitamos un **cliente HTTP**. `httpx` es como
`requests` pero **asíncrono**, lo que encaja con `python-telegram-bot`.

### Cambios

1. Nuevo archivo `bot/api_client.py`:

   ```python
   """Cliente HTTP asíncrono para PokeAPI."""
   from __future__ import annotations

   import os

   import httpx

   BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2")


   async def get_pokemon(nombre_o_id: str) -> dict:
       """Busca un pokémon por nombre o id. Lanza HTTPStatusError si no existe."""
       async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
           r = await client.get(f"/pokemon/{nombre_o_id.lower()}")
           r.raise_for_status()
           return r.json()
   ```

2. `requirements.txt`:

   ```diff
    python-telegram-bot>=21.0
    python-dotenv>=1.0.1
   + httpx>=0.27.0
   ```

### Commit sugerido

```bash
git add .
git commit -m "v2: cliente HTTP httpx para PokeAPI"
```

### Narrativa en clase

> "Ahora el bot va a **preguntarle algo a otro servidor**. La librería
> `httpx` es como `requests` pero habla **async**. Veamos cómo se
> usa en una línea: `curl` por un lado y `httpx.AsyncClient` por el
> otro hacen exactamente lo mismo."

**Demuestra** (en otra terminal):

```bash
curl https://pokeapi.co/api/v2/pokemon/pikachu | head
```

Mostrar que la salida es JSON enorme: ~150 campos.

---

## v3 — Primer comando que consulta la API

### Concepto

- Los comandos reciben argumentos en `ctx.args` (lista de strings).
- Cuando un comando llama a una API puede **fallar** (404, timeout,
  sin internet). Hay que manejar el error.

### Cambios

`bot/__main__.py`:

```diff
  from telegram import Update
  from telegram.ext import Application, CommandHandler, ContextTypes
  import os
+ import httpx
  from dotenv import load_dotenv

  load_dotenv()
  TOKEN = os.getenv("TELEGRAM_TOKEN")

+ from bot.api_client import get_pokemon


  async def hola(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
      await update.message.reply_text("Hola mundo 👋")


+ async def poke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
+     if not ctx.args:
+         await update.message.reply_text("Uso: /poke <nombre_o_id>")
+         return
+     nombre = ctx.args[0]
+     try:
+         data = await get_pokemon(nombre)
+     except httpx.HTTPStatusError:
+         await update.message.reply_text(f"❌ No encontré '{nombre}'")
+         return
+     await update.message.reply_text(f"Encontré: {data['name']}")


  def main():
      app = Application.builder().token(TOKEN).build()
      app.add_handler(CommandHandler("start", hola))
+     app.add_handler(CommandHandler("poke", poke))
      app.run_polling()
```

### Commit sugerido

```bash
git add .
git commit -m "v3: comando /poke que consulta PokeAPI"
```

### Narrativa en clase

> "El bot ya habla con internet. Si le pido `/poke pikachu` me
> devuelve algo. Si le pido `/poke noexiste` la API responde 404
> y **mi código revienta** si no lo manejo. Por eso el `try/except`."

**Pruebas en vivo**:
- `/poke pikachu` → "Encontré: pikachu"
- `/poke 25` → "Encontré: pikachu" (también funciona por id)
- `/poke noexiste` → "❌ No encontré 'noexiste'"
- `/poke` (sin argumentos) → "Uso: /poke <nombre_o_id>"

---

## v4 — Formatear la respuesta

### Concepto

La API devuelve ~150 campos. **No los mostramos todos**. Decidimos
cuáles son útiles para el usuario y los formateamos con **Markdown**
(negritas, emojis, etc.).

### Cambios

`bot/__main__.py`:

```diff
-     await update.message.reply_text(f"Encontré: {data['name']}")
+     tipos = ", ".join(t["type"]["name"] for t in data["types"])
+     texto = (
+         f"🔎 *{data['name'].title()}* (#{data['id']})\n"
+         f"Tipo: {tipos}\n"
+         f"Altura: {data['height']/10} m\n"
+         f"Peso: {data['weight']/10} kg"
+     )
+     await update.message.reply_text(texto, parse_mode="Markdown")
```

Para entender mejor el JSON:

```bash
curl -s https://pokeapi.co/api/v2/pokemon/pikachu | python -m json.tool | head -30
```

Mostrar que `types`, `height`, `weight` son las claves que nos
interesan.

### Commit sugerido

```bash
git commit -m "v4: formatear respuesta con markdown y emojis"
```

### Narrativa en clase

> "La PokeAPI devuelve **150 campos** sobre cada pokémon. No
> podemos mostrar todos: sería ilegible. Elegimos los más importantes
> (tipos, altura, peso) y los formateamos con negritas y emojis.
> **El formateo es una decisión de diseño**, no técnica."

---

## v5 — Inline keyboard (botones)

### Concepto

Telegram distingue **dos tipos de teclado**:

- **Reply keyboard**: botones en el teclado del teléfono (abajo del
  campo de texto).
- **Inline keyboard**: botones **adjuntos a un mensaje específico**.
  Cuando el usuario pulsa, Telegram envía un `callback_query` al bot.

Cada botón lleva un `callback_data` (string corto, idealmente con un
prefijo). El bot registra un `CallbackQueryHandler` con un patrón
regex.

### Cambios

`bot/__main__.py`:

```diff
  from telegram import Update
- from telegram.ext import Application, CommandHandler, ContextTypes
+ from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
+ from telegram.ext import (
+     Application, CallbackQueryHandler, CommandHandler, ContextTypes,
+ )

  # ...

  async def poke(update, ctx):
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
+     teclado = InlineKeyboardMarkup([
+         [InlineKeyboardButton("📊 Ver stats", callback_data="stats")],
+     ])
      await update.message.reply_text(
          texto,
+         reply_markup=teclado,
          parse_mode="Markdown",
      )

+ async def boton_stats(update, ctx):
+     q = update.callback_query
+     await q.answer()  # quita el "loading" del botón
+     await q.edit_message_text("📊 (Acá mostraremos los stats...)")


  def main():
      app = Application.builder().token(TOKEN).build()
      app.add_handler(CommandHandler("start", hola))
      app.add_handler(CommandHandler("poke", poke))
+     app.add_handler(CallbackQueryHandler(boton_stats, pattern="^stats$"))
      app.run_polling()
```

### Commit sugerido

```bash
git commit -m "v5: inline keyboard con boton de stats"
```

### Narrativa en clase

> "Acá viene lo más vistoso de un bot de Telegram: los **botones
> inline**. Hay dos tipos de teclado en Telegram: los que están
> abajo del campo de texto (reply keyboard) y los que van pegados al
> mensaje (inline). Estos últimos envían un **callback** al bot
> cuando los pulsas."

**Demuestra**: `/poke pikachu` → mostrar los botones → pulsar
"📊 Ver stats" → ver cómo Telegram quita el "loading" del botón y
el bot responde.

---

## v6 — Botones que llaman distintos endpoints

### Concepto

`callback_data` puede llevar **datos**: `stats:25`, `spr:25`. Un solo
`CallbackQueryHandler` puede atender muchos botones distintos
usando un patrón regex y separando el `data` por `:`.

### Cambios

Guardamos el pokémon actual en `ctx.user_data` para no tener que
volver a llamar la API cuando el usuario pulsa un botón.

`bot/__main__.py`:

```diff
  async def poke(update, ctx):
      if not ctx.args:
          await update.message.reply_text("Uso: /poke <nombre_o_id>")
          return
      nombre = ctx.args[0]
      try:
          data = await get_pokemon(nombre)
      except httpx.HTTPStatusError:
          await update.message.reply_text(f"❌ No encontré '{nombre}'")
          return

+     ctx.user_data["ultimo_pokemon"] = data

      tipos = ", ".join(t["type"]["name"] for t in data["types"])
      texto = (
          f"🔎 *{data['name'].title()}* (#{data['id']})\n"
          f"Tipo: {tipos}\n"
          f"Altura: {data['height']/10} m\n"
          f"Peso: {data['weight']/10} kg"
      )
-     teclado = InlineKeyboardMarkup([
-         [InlineKeyboardButton("📊 Ver stats", callback_data="stats")],
-     ])
+     teclado = InlineKeyboardMarkup([
+         [InlineKeyboardButton("📊 Stats", callback_data="stats"),
+          InlineKeyboardButton("🎨 Sprite", callback_data="sprite")],
+     ])
      await update.message.reply_text(texto, reply_markup=teclado, parse_mode="Markdown")


- async def boton_stats(update, ctx):
+ async def botones_pokemon(update, ctx):
      q = update.callback_query
      await q.answer()
+     data = ctx.user_data.get("ultimo_pokemon")
+     if not data:
+         await q.edit_message_text("⚠️ Primero usa /poke")
+         return
+     accion = q.data
+     if accion == "stats":
+         stats = "\n".join(
+             f"• {s['stat']['name']}: {s['base_stat']}"
+             for s in data["stats"]
+         )
+         await q.edit_message_text(f"📊 *Stats de {data['name'].title()}*\n\n{stats}",
                                   parse_mode="Markdown")
+     elif accion == "sprite":
+         url = data["sprites"]["front_default"]
+         await q.edit_message_text(f"🎨 {url or 'Sin sprite'}")

  def main():
      app = Application.builder().token(TOKEN).build()
      app.add_handler(CommandHandler("start", hola))
      app.add_handler(CommandHandler("poke", poke))
-     app.add_handler(CallbackQueryHandler(boton_stats, pattern="^stats$"))
+     app.add_handler(CallbackQueryHandler(botones_pokemon, pattern="^(stats|sprite)$"))
      app.run_polling()
```

### Commit sugerido

```bash
git commit -m "v6: botones llaman distintos endpoints (stats y sprite)"
```

### Narrativa en clase

> "Acá viene la parte **clave**: el botón no tiene que ser estático.
> Cuando el usuario lo pulsa, **el bot puede llamar a la API otra
> vez** y editar el mensaje con la nueva información. El
> `callback_data` puede llevar datos: `stats:25`, `sprite:25`. Eso
> permite que un solo handler atienda muchos botones."

**Demuestra**:
1. `/poke pikachu`
2. Pulsar "📊 Stats" → aparecen los stats
3. `/poke pikachu` (otra vez)
4. Pulsar "🎨 Sprite" → aparece la URL del sprite

---

## v7 — Manejo robusto de errores

### Concepto

Un bot en producción debe responder a **cualquier** error sin
morirse. Si la API está caída, el timeout se dispara, el JSON viene
mal, etc. → mostrar mensaje elegante.

### Cambios

`bot/api_client.py`:

```diff
  """Cliente HTTP asíncrono para PokeAPI."""
  from __future__ import annotations

  import os

  import httpx

  BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2")


+ class APIError(Exception):
+     """Error genérico al hablar con una API externa."""


  async def get_pokemon(nombre_o_id: str) -> dict:
-     """Busca un pokémon por nombre o id. Lanza HTTPStatusError si no existe."""
      async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
          try:
              r = await client.get(f"/pokemon/{nombre_o_id.lower()}")
              r.raise_for_status()
          except httpx.HTTPStatusError as e:
              raise APIError(f"No encontrado: {nombre_o_id}") from e
          except httpx.RequestError as e:
              raise APIError("Sin conexión a la API") from e
          return r.json()
```

`bot/__main__.py`:

```diff
  from bot.api_client import get_pokemon
+ from bot.api_client import APIError, get_pokemon

  # ...

  async def poke(update, ctx):
      if not ctx.args:
          await update.message.reply_text("Uso: /poke <nombre_o_id>")
          return
      nombre = ctx.args[0]
      try:
          data = await get_pokemon(nombre)
-     except httpx.HTTPStatusError:
-         await update.message.reply_text(f"❌ No encontré '{nombre}'")
+     except APIError as e:
+         await update.message.reply_text(f"❌ {e}")
          return
```

### Commit sugerido

```bash
git commit -m "v7: manejo de errores con clase APIError"
```

### Narrativa en clase

> "Si la API está caída o tarda demasiado, el bot **antes** mostraba
> un traceback larguísimo en los logs y el usuario veía un mensaje
> raro. Ahora **capturamos el error, lo convertimos en un mensaje
> corto y legible**, y el bot sigue funcionando para el siguiente
> usuario."

---

## v8 — Lista paginada (`/pokemones`)

### Concepto

Hasta ahora `/poke` requiere que el usuario **sepa** el nombre o número
del pokémon. Pero PokeAPI tiene **1351 pokémons**: nadie se los sabe
de memoria. Vamos a agregar un comando `/pokemones` que muestra
**páginas de 20 nombres** con botones `« Anterior` / `Siguiente »`.

Conceptos nuevos:
- **Parámetros en GET**: PokeAPI acepta `?offset=N&limit=20` para
  paginar resultados.
- **Estado en callback_data**: el botón lleva el `offset` dentro del
  string (`lista:20`, `lista:40`).
- **Render dinámico del teclado**: dependiendo de si hay `next` /
  `previous` en la respuesta de PokeAPI, mostramos o no los botones.

### Cambios

`bot/api_client.py`:

```diff
  BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2")


+ PAGE_SIZE = 20
+
+
  class APIError(Exception):
      """Error generico al hablar con una API externa."""


+ async def _get(client, path, **params):
+     try:
+         r = await client.get(path, params=params or None)
+         r.raise_for_status()
+     except httpx.HTTPStatusError as e:
+         raise APIError(f"Error HTTP {r.status_code}") from e
+     except httpx.RequestError as e:
+         raise APIError("Sin conexion a la API") from e
+     return r.json()
+
+
  async def get_pokemon(nombre_o_id: str) -> dict:
-     async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
-         try:
-             r = await client.get(f"/pokemon/{nombre_o_id.lower()}")
-             r.raise_for_status()
-         except httpx.HTTPStatusError as e:
-             raise APIError(f"No encontrado: {nombre_o_id}") from e
-         except httpx.RequestError as e:
-             raise APIError("Sin conexion a la API") from e
-         return r.json()
+     async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
+         return await _get(client, f"/pokemon/{nombre_o_id.lower()}")
+
+
+ async def listar_pokemones(offset: int = 0, limit: int = PAGE_SIZE) -> dict:
+     """Devuelve una pagina con metadata de paginacion:
+       { count, next, previous, results: [{name, url}] }
+     """
+     async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
+         return await _get(client, "/pokemon", offset=offset, limit=limit)
```

`bot/__main__.py`:

```diff
- from bot.api_client import APIError, get_pokemon
+ from bot.api_client import APIError, PAGE_SIZE, get_pokemon, listar_pokemones

+ def _render_lista(data: dict) -> tuple[str, InlineKeyboardMarkup]:
+     nombres = [p["name"] for p in data["results"]]
+     if data["next"]:
+         offset_actual = int(data["next"].split("offset=")[1].split("&")[0]) - PAGE_SIZE
+     else:
+         offset_actual = data["count"] - len(nombres)
+     inicio = offset_actual + 1
+     fin = offset_actual + len(nombres)
+     total = data["count"]
+
+     texto = (
+         f"📜 *Pokémons {inicio}–{fin} de {total}*\n"
+         f"_Copiá uno y usá:_ `/poke nombre`\n\n"
+     )
+     nombres_fmt = [f"`{n}`" for n in nombres]
+     filas = []
+     for i in range(0, len(nombres_fmt), 2):
+         fila = nombres_fmt[i:i+2]
+         filas.append("  ".join(fila))
+     texto += "\n".join(filas)
+
+     botones = []
+     if data["previous"]:
+         prev_offset = max(0, offset_actual - PAGE_SIZE)
+         botones.append(InlineKeyboardButton("« Anterior",
+ callback_data=f"lista:{prev_offset}"))
+     botones.append(InlineKeyboardButton(f"{fin}/{total}",
+ callback_data="noop"))
+     if data["next"]:
+         next_offset = offset_actual + PAGE_SIZE
+         botones.append(InlineKeyboardButton("Siguiente »",
+ callback_data=f"lista:{next_offset}"))
+     return texto, InlineKeyboardMarkup([botones])
+
+
+ async def pokemones(update, ctx):
+     offset = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() else 0
+     try:
+         data = await listar_pokemones(offset=offset)
+     except APIError as e:
+         await update.message.reply_text(f"❌ {e}")
+         return
+     texto, teclado = _render_lista(data)
+     await update.message.reply_text(texto, reply_markup=teclado,
+ parse_mode="Markdown")
+
+
+ async def callback_lista(update, ctx):
+     q = update.callback_query
+     await q.answer()
+     if q.data == "noop":
+         return
+     if not q.data.startswith("lista:"):
+         return
+     offset = int(q.data.split(":", 1)[1])
+     try:
+         data = await listar_pokemones(offset=offset)
+     except APIError as e:
+         await q.edit_message_text(f"❌ {e}")
+         return
+     texto, teclado = _render_lista(data)
+     await q.edit_message_text(texto, reply_markup=teclado,
+ parse_mode="Markdown")

  def main():
      app = Application.builder().token(TOKEN).build()
      app.add_handler(CommandHandler("start", hola))
      app.add_handler(CommandHandler("poke", poke))
+     app.add_handler(CommandHandler("pokemones", pokemones))
      app.add_handler(CallbackQueryHandler(botones_pokemon,
 pattern="^(stats|sprite)$"))
+     app.add_handler(CallbackQueryHandler(callback_lista,
 pattern=r"^(lista:|noop)"))
      app.run_polling(allowed_updates=Update.ALL_TYPES)
```

### Commit sugerido

```bash
git commit -m "v8: comando /pokemones con paginacion (lista 1351 pokemones)"
```

### Narrativa en clase

> "PokeAPI tiene 1351 pokémons. Nadie se los sabe de memoria.
> Agregamos un comando `/pokemones` que muestra páginas de 20 nombres.
> Los botones `« Anterior` y `Siguiente »` llevan el `offset` dentro
> del `callback_data` (`lista:0`, `lista:20`, `lista:40`...). Cuando
> el usuario pulsa uno, el bot **vuelve a llamar la API** con el
> nuevo offset y reemplaza el mensaje con la siguiente página."

**Demuestra**:
1. `/pokemones` → muestra bulbasaur, ivysaur, venusaur, ...
2. Pulsar **Siguiente »** → charmander, charmeleon, charizard, ...
3. Navegar varias páginas (ver cómo cambia el contador `20/1351`,
   `40/1351`, ...)
4. Intentar `/pokemones 1330` → salta a las últimas páginas (Zygarde,
   ...)

### Comportamiento de los botones

| Caso | Botones que se muestran |
|---|---|
| Primera página (offset 0) | `[ 20/1351 ]  [Siguiente »]` |
| Página intermedia | `[« Anterior]  [600/1351]  [Siguiente »]` |
| Última página | `[« Anterior]  [1351/1351]` |
| Una sola página | `[1351/1351]` (sin flechas) |

El botón del medio (`noop`) **no hace nada** cuando se pulsa — está
solo como indicador visual de progreso.

---

## Cierre y preguntas frecuentes

### Resumen visual de la evolución

```
v0: bot tonto (hola mundo)
        ↓
v1: secrets en .env
        ↓
v2: cliente HTTP
        ↓
v3: comando que llama API
        ↓
v4: respuesta formateada
        ↓
v5: ⭐ inline keyboard
        ↓
v6: ⭐⭐ botones que llaman API
        ↓
v7: errores elegantes
        ↓
v8: lista paginada con « Ant / Sig »
```

### Posibles preguntas en clase

**P: ¿Necesito un servidor donde correr el bot?**
R: No. Con `python-telegram-bot` y un `run_polling()` el bot habla
directamente con los servidores de Telegram. Para producción se
recomienda un servidor propio o un servicio como Railway/Render.

**P: ¿Y si quiero que más gente use el bot?**
R: Cualquiera puede encontrarlo por su `@nombre` y hablarle. El bot
no restringe por usuario a menos que tú pongas un whitelist con
`filters.User(user_id=[...])`.

**P: ¿Y si la API tiene API key?**
R: Se guarda en `.env` igual que el `TELEGRAM_TOKEN` y se lee con
`os.getenv()`. Nunca hardcodear.

**P: ¿Y si quiero guardar datos en mi propia base de datos?**
R: Eso ya es un proyecto con API propia (FastAPI + Postgres). El bot
`academia-bots` que vimos antes hace ese patrón completo.

---

## Cronograma sugerido

| Tiempo | Actividad |
|---|---|
| 0:00 | Intro: mostrar v0 y explicar la idea de la demo |
| 0:03 | v1: secretos, `.env`, `.gitignore` |
| 0:08 | v2: cliente HTTP, mostrar `curl` paralelo |
| 0:13 | v3: primer comando que llama la API |
| 0:18 | v4: formatear la respuesta |
| 0:23 | v5: ⭐ inline keyboard |
| 0:30 | v6: ⭐⭐ callbacks que llaman la API |
| 0:37 | v7: manejo de errores |
| 0:40 | v8: lista paginada `/pokemones` |
| 0:45 | Resumen, preguntas, cierre |

**Total: 45 minutos** (más 10 min de buffer para preguntas).