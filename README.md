# PokeBot 🐢 — Demo pedagógica

Bot de Telegram usado como ejemplo en la exposición. Empieza como un
"Hola Mundo" y se va **evolucionando commit por commit** hasta
convertirse en un bot que **consulta la PokeAPI** y **crea posts en
JSONPlaceholder** usando botones inline.

## Arranque rápido

1. **Crear el bot en Telegram**: habla con [@BotFather](https://t.me/BotFather),
   usa `/newbot`, copia el token.

2. **Pegar el token en `.env`**:
   ```env
   TELEGRAM_TOKEN=123456789:ABCdef...tu_token_real
   ```

3. **Crear entorno virtual e instalar dependencias**:
   ```bash
   cd pokebot
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Ejecutar el bot**:
   ```bash
   python -m bot
   ```

5. **Probar**: abre Telegram, busca tu bot por su `@nombre` y envía `/start`.
   Debería responder `Hola mundo 👋`.

## Estructura

```
pokebot/
├── .env                    ← tu token real (NO se sube a git)
├── .env.example            ← plantilla (sí se sube)
├── .gitignore
├── README.md
├── requirements.txt
└── bot/
    ├── __init__.py
    └── __main__.py         ← entrypoint (v0: hola mundo)
```

## Evolución pedagógica

El plan completo está en **`../plan_pedagogico_bot.md`** (carpeta
padre `exposicion/`). Cada commit agrega un único cambio:

1. **v1**: leer token desde `.env`
2. **v2**: cliente HTTP con `httpx`
3. **v3**: comando `/poke` que consulta PokeAPI
4. **v4**: formatear respuesta
5. **v5**: ⭐ inline keyboard
6. **v6**: ⭐⭐ botones que llaman la API
8. **v7**: ⭐⭐⭐ POST para crear un post
9. **v8**: manejo de errores

## Comandos (v0)

| Comando | Respuesta |
|---|---|
| `/start` | `Hola mundo 👋` |

## API usada durante la evolución

- **[PokeAPI](https://pokeapi.co)** — para los `/poke` y botones.
- **[JSONPlaceholder](https://jsonplaceholder.typicode.com)** — para
  el POST de creación de posts (v7).

Ambas son **gratuitas, sin API key**.

## Notas

- El `.env` ya viene con un placeholder. Solo reemplaza la línea
  `TELEGRAM_TOKEN=...` por tu token real.
- El plan asume que `python-telegram-bot` v21+ se ejecuta en **modo
  polling** (no necesitas servidor).
- Si tienes firewall/proxy, `python-telegram-bot` necesita salida a
  `api.telegram.org` (puerto 443).