# PokeBot 🐢 — Demo pedagógica

Bot de Telegram usado como ejemplo en la exposición. Empieza como un
"Hola Mundo" y se va **evolucionando commit por commit** hasta
convertirse en un bot que **consulta la PokeAPI** (búsqueda individual
y lista paginada) usando botones inline.

## Arranque rápido (paso a paso)

### 1. Crear el bot en Telegram

1. Abre Telegram y busca **@BotFather**.
2. Envíale `/newbot`.
3. Elige un **nombre** visible para el bot (ej: `Mi PokeBot`).
4. Elige un **username** único terminado en `bot` (ej: `mi_pokebot`).
5. BotFather te responde con un **token** largo tipo:
   ```
   123456789:AAHadnii_mvisT0UqiE-qgi90HYgBrsKd4Q
   ```
   **Cópialo**, lo vas a pegar en `.env`.

> ⚠️ **Importante**: ese token da control total sobre tu bot.
> **No lo subas al repo ni lo pegues en chats**. Si se filtra, usa
> `@BotFather` → `/revoke` para invalidarlo.

### 2. Pegar el token en `.env`

Abre `.env` (ya existe con un placeholder) y reemplaza:

```env
TELEGRAM_TOKEN=PEGA_AQUI_TU_TOKEN_DE_BOTFATHER
```

por:

```env
TELEGRAM_TOKEN=123456789:AAHadnii_mvisT0UqiE-qgi90HYgBrsKd4Q
```

Solo esa línea. `.env` está en `.gitignore`, no se sube a GitHub.

### 3. Crear el entorno virtual e instalar dependencias

```bash
cd pokebot

# Crear el venv
python -m venv .venv

# Activarlo
# Linux / Mac:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat

# Instalar las dependencias (las 3 que se agregaron en v1, v2 y v7)
pip install -r requirements.txt
```

Verás que `requirements.txt` ahora pide:

```
python-telegram-bot>=21.0   # el framework del bot
python-dotenv>=1.0.1        # para leer el .env (v1)
httpx>=0.27.0               # cliente HTTP async (v2)
```

Si tu `python` por defecto no encuentra `venv` en Debian/Ubuntu:

```bash
sudo apt install python3-venv
```

### 4. Ejecutar el bot

```bash
python -m bot
```

Salida esperada:

```
2026-09-28 22:00:00,000 telegram.ext.Application [INFO] Application started
2026-09-28 22:00:01,234 telegram.ext.Application [INFO] Bot poked!
```

Si ves errores tipo `Invalid token`, vuelve al paso 2.

### 5. Probarlo en tu teléfono

1. Abre Telegram, busca tu bot por su **@username** (ej: `@mi_pokebot`).
2. Pulsa **Start** o envía `/start`.
3. Comandos disponibles:
   - `/start` → menú con los comandos
   - `/pokemones` → lista paginada (1351 pokémons)
   - `/poke pikachu` → ficha del pokémon con tipos, altura, peso
   - `/poke 25` → igual pero por id numérico
   - `/poke noexiste` → `❌ No encontrado: noexiste`
   - Pulsar **Siguiente »** en la lista → siguiente página
   - Pulsar **« Anterior** → página anterior
   - Pulsar **📊 Stats** o **🎨 Sprite** debajo de `/poke` → más datos

### 6. Detener el bot

`Ctrl + C` en la terminal donde lo arrancaste.

> **¿Por qué se queda bloqueada la terminal?**
> `run_polling()` es un loop infinito que mantiene el bot
> escuchando mensajes de Telegram. Solo termina con `Ctrl + C`.

---

## Estructura del repo

```
pokebot/
├── .env                 ← tu token real (NO se sube a git)
├── .env.example         ← plantilla (sí se sube)
├── .gitignore
├── README.md
├── requirements.txt
└── bot/
    ├── __init__.py
    ├── __main__.py      ← entrypoint + handlers
    └── api_client.py    ← cliente HTTP a PokeAPI (con GET individual y paginado)
```

## Evolución pedagógica (commits)

El plan completo está en **`../plan_pedagogico_bot.md`** (carpeta
padre `exposicion/`). Cada commit agrega un único cambio:

| Commit | Concepto |
|---|---|
| **v0** | Hola mundo |
| **v1** | leer token desde `.env` |
| **v2** | cliente HTTP con `httpx` |
| **v3** | comando `/poke` que consulta PokeAPI |
| **v4** | formatear respuesta |
| **v5** | ⭐ inline keyboard |
| **v6** | ⭐⭐ botones que llaman la API |
| **v7** | manejo de errores |
| **v8** | ⭐⭐⭐ lista paginada (`/pokemones`) |

### Ver el historial

```bash
git log --oneline
```

### Ver el diff de un commit

```bash
git show ae7550c    # v7: manejo de errores
git show 957886a    # v8: lista paginada
```

### Volver al estado de una versión específica

Hay **3 formas**, de menos a más invasiva:

#### A) Solo mirar (no toca archivos)

```bash
git show <hash>:<archivo>
```

Ejemplo:

```bash
git show ae7550c:bot/api_client.py  # ver api_client.py en v7
```

#### B) Volver a un commit **sin perder nada** (modo detached)

```bash
git checkout <hash>
```

Ejemplos:

```bash
git checkout c3220c4   # volver al hola mundo (v0)
git checkout 9596ac7   # volver al estado de v1
git checkout 957886a   # volver al estado de v8 (con /pokemones)
```

En modo detached podés leer y probar el código, pero cualquier cambio
que hagas **no se queda en una rama**. Para volver a la rama `main`:

```bash
git checkout main
```

#### C) Crear una rama nueva desde un commit

```bash
git checkout -b demo-clase <hash>
```

Ejemplo:

```bash
git checkout -b demo-clase fa90d86  # rama con el código de v4
```

### Navegar commit por commit (útil para mostrar en clase)

```bash
git checkout c3220c4    # v0
git checkout 9596ac7    # v1
git checkout 81af8e8    # v2
git checkout e22a8f8    # v3
git checkout fa90d86    # v4
git checkout 275ec82    # v5
git checkout 6a98ac2    # v6
git checkout ae7550c    # v7
git checkout 957886a    # v8
git checkout main       # estado final (con menú /start)
```

Atajo con `git checkout HEAD~N`:

```bash
git checkout HEAD     # estado actual
git checkout HEAD~1   # 1 commit atrás
git checkout HEAD~8   # vuelve al v0
```

### Reset duro (⚠️ borra cambios locales)

Solo si querés **borrar todo y volver al commit `inicial`**:

```bash
git reset --hard c3220c4
```

### Comparar dos commits

```bash
git diff v0 v8                # todos los cambios entre v0 y v8
git diff 81af8e8 e22a8f8      # cambios entre v2 y v3
git diff main v3              # qué tendrías que quitar para volver a v3
```

## API usada

- **[PokeAPI](https://pokeapi.co)** — para `/poke`, `/pokemones` y botones.
  Sin auth, sin key. 1351 pokémons disponibles.

## Troubleshooting

| Problema | Causa probable | Solución |
|---|---|---|
| `python: command not found` | Python no instalado | Instala Python 3.10+ |
| `No module named 'venv'` | Debian/Ubuntu sin `python3-venv` | `sudo apt install python3-venv` |
| `RuntimeError: Falta TELEGRAM_TOKEN en el .env` | `.env` sin el token real | Revisa el paso 2 |
| `Invalid token` | Token mal copiado | Vuelve a pedirlo a @BotFather |
| `No such file or directory: '.env'` | No estás en la carpeta `pokebot/` | `cd pokebot` |
| `pip install` falla con permisos | venv no activado | Activa el venv (paso 3) |
| Terminal queda colgada con `python -m bot` | Normal: `run_polling()` bloquea | `Ctrl + C` para detenerlo |