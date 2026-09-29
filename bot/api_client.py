"""Cliente HTTP asincrono para PokeAPI."""
from __future__ import annotations

import os

import httpx

BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2")

PAGE_SIZE = 20


class APIError(Exception):
    """Error generico al hablar con una API externa."""


async def _get(client: httpx.AsyncClient, path: str, **params) -> dict:
    try:
        r = await client.get(path, params=params or None)
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise APIError(f"Error HTTP {r.status_code}") from e
    except httpx.RequestError as e:
        raise APIError("Sin conexion a la API") from e
    return r.json()


async def get_pokemon(nombre_o_id: str) -> dict:
    async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
        return await _get(client, f"/pokemon/{nombre_o_id.lower()}")


async def listar_pokemones(offset: int = 0, limit: int = PAGE_SIZE) -> dict:
    """Devuelve una pagina de pokemones con metadata de paginacion.

    Respuesta de PokeAPI:
      {
        "count": 1351,
        "next": "https://...?offset=20&limit=20",
        "previous": null,
        "results": [{"name": "...", "url": "..."}]
      }
    """
    async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
        return await _get(client, "/pokemon", offset=offset, limit=limit)