"""Cliente HTTP asincrono para PokeAPI."""
from __future__ import annotations

import os

import httpx

BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2")


class APIError(Exception):
    """Error generico al hablar con una API externa."""


async def get_pokemon(nombre_o_id: str) -> dict:
    async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
        try:
            r = await client.get(f"/pokemon/{nombre_o_id.lower()}")
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(f"No encontrado: {nombre_o_id}") from e
        except httpx.RequestError as e:
            raise APIError("Sin conexion a la API") from e
        return r.json()