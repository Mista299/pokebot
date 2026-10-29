# Colección Insomnia — PokeAPI (PokeBot)

Configuración lista para probar en **Insomnia** los endpoints que llama
el bot de Telegram. Cada request corresponde a una llamada real de
`bot/api_client.py`.

## Cómo importar

1. Abrí Insomnia → **Preferences** → **Data** → **Import**
2. Seleccioná el archivo `PokeBot-PokeAPI.insomnia.json`
3. Se crea el workspace **PokeBot** con 3 carpetas y 10 requests
4. Activá el entorno **PokeAPI** (arriba a la derecha)

> **Si te dice "No importers found for file"**: estás usando un archivo
> con la estructura vieja (`collection` anidado). El formato v4 de
> Insomnia espera un array plano `resources` donde cada elemento lleva
> su `_type` (`workspace`, `request_group`, `environment`, `request`).
> Este archivo ya usa ese formato.

### Estructura del archivo

```
PokeBot-PokeAPI.insomnia.json
├── __export_format: 4
└── resources: [ ... ]          ← array PLANO, cada uno con su _type
    ├── _type: workspace        → el workspace "PokeBot"
    ├── _type: environment       → el entorno "PokeAPI"
    ├── _type: request_group     → las 3 carpetas
    └── _type: request           → los 10 requests
```


## El entorno

| Variable | Valor | Para qué |
|---|---|---|
| `base_url` | `https://pokeapi.co/api/v2` | La base, igual que `POKEAPI_BASE` en el `.env` |
| `page_size` | `20` | Items por página, igual que `PAGE_SIZE` en `api_client.py` |
| `total_pokemon` | `1351` | Total de la pokedex |

`page_size` se usa como `{{page_size}}` en el query param `limit`, así
si cambiás el valor en el entorno, cambiás el `limit` de todos los
requests de golpe. Es el mismo concepto que la constante `PAGE_SIZE`.

---

## Las 3 carpetas

### 1. Pokemon individual — `get_pokemon()`

`GET /pokemon/{nombre_o_id}` — lo usa el comando `/poke`

| Request | URL | Comando del bot |
|---|---|---|
| Buscar por nombre | `/pokemon/pikachu` | `/poke pikachu` |
| Buscar por id | `/pokemon/25` | `/poke 25` |
| Nombre compuesto | `/pokemon/meowstic-female-mega` | — |

**Claves del JSON que usa el bot:**

```
data['name']      -> el nombre
data['id']        -> el número en la pokedex
data['types']     -> los tipos (electric, ...)
data['height']    -> altura en decímetros  (/10 = metros)
data['weight']    -> peso en hectogramos  (/10 = kg)
data['stats']     -> las 6 stats base      (botón "Ver stats")
data['sprites']   -> URLs de imágenes      (botón "Ver sprite")
```

> **Dato útil**: el bot aplica `.lower()` al nombre, pero PokeAPI
> **igual acepta mayúsculas**. `GET /pokemon/Pikachu` → HTTP 200 y
> devuelve `name: "pikachu"`. No es culpa del `.lower()` del bot.

### 2. Lista paginada — `listar_pokemones()`

`GET /pokemon?offset=&limit=` — lo usa el comando `/pokemones`

| Request | offset | limit | Qué muestra el bot |
|---|---|---|---|
| Primera página | 0 | 20 | `Pokémons 1–20 de 1351` + `[20/1351] [Siguiente »]` |
| Página del medio | 40 | 20 | `Pokémons 41–60 de 1351` + `[« Anterior] [60/1351] [Siguiente »]` |
| Última página | 1340 | 20 | `Pokémons 1341–1351 de 1351` + `[« Anterior] [1351/1351]` |
| Limite grande | 0 | 1000 | Los 1351 de una vez |

**Estructura de la respuesta:**

```json
{
  "count": 1351,
  "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
  "previous": null,
  "results": [{ "name": "bulbasaur", "url": "..." }, ...]
}
```

`next` y `previous` vienen con el offset **ya calculado en la URL**.
El bot no usa esos números directo: los parsea con

```python
offset_actual = int(data["next"].split("offset=")[1].split("&")[0]) - PAGE_SIZE
```

En la **última página** `next` es `null`, y ahí el bot usa el otro
cálculo:

```python
offset_actual = data["count"] - len(nombres)   # 1351 - 11 = 1340
```

### 3. Casos de error — `APIError`

| Request | Resultado | Qué hace el bot |
|---|---|---|
| `GET /pokemon/noexiste` | **HTTP 404** | `raise_for_status()` → `HTTPStatusError` → `APIError("Error HTTP 404")` |
| `GET /pokemon?offset=9999` | HTTP 200, `results: []` | No es error. El bot lo renderiza raro pero no crashea |
| Host inválido | `RequestError` | → `APIError("Sin conexion a la API")` |

**La distinción clave** (son dos ramas distintas del `except`):

| Excepción | Cuándo | Mensaje del bot |
|---|---|---|
| `httpx.HTTPStatusError` | La API **respondió** (404, 500) | `Error HTTP 404` |
| `httpx.RequestError` | La API **no respondió** (timeout, sin DNS) | `Sin conexion a la API` |

Para simular el segundo caso, editá la URL de cualquier request y poné
un host que no exista:

```
https://pokeapi.invalid/api/v2/pokemon/pikachu
```

> ⚠️ **El bot nunca ve el 404 crudo.** `raise_for_status()` lo
> convierte en `HTTPStatusError`, y `api_client.py` lo traduce a
> `APIError` con un mensaje legible para el usuario.

---

## Comparar Insomnia vs el bot

Son **exactamente** la misma llamada. Para verlo, dejá el bot corriendo
en una terminal y la request de Insomnia en otra:

```bash
# Terminal 1 — el bot
python -m bot

# Terminal 2 — la misma llamada, pero sin el bot
curl -s https://pokeapi.co/api/v2/pokemon/pikachu | python -m json.tool | head -20
```

El bot usa `httpx.AsyncClient` con `base_url=BASE` y `timeout=10.0`.
Insomnia hace lo mismo pero a mano, en un request sincrónico.

| | Bot (httpx) | Insomnia |
|---|---|---|
| URL base | `BASE` del `.env` | variable `base_url` |
| Timeout | `10.0` segundos | se configura en Settings |
| Errores | `APIError` (propia) | los muestra el cliente |
| Async | ✅ `await` | ❌ sincrónico |

---

## Referencia rápida de la API

- Docs: https://pokeapi.co/docs/v2
- Base: `https://pokeapi.co/api/v2`
- Sin API key, sin registro, sin límite de requests
- Total: 1351 pokémons

| Endpoint | Devuelve |
|---|---|
| `GET /pokemon/{name\|id}` | Ficha completa de un pokémon |
| `GET /pokemon?offset=&limit=` | Lista paginada |
| `GET /pokemon/{name}/species` | Datos de la especie |
| `GET /pokemon/{name}/{ability}` | Detalle de una habilidad |
| `GET /type/{type}` | Detalle de un tipo |
| `GET /ability/{ability}` | Detalle de una habilidad |
