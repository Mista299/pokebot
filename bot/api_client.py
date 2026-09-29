"""Cliente HTTP asincrono para PokeAPI."""
from __future__ import annotations

import os

import httpx

BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2")


async def get_pokemon(nombre_o_id: str) -> dict:
    """Busca un pokemon por nombre o id. Lanza HTTPStatusError si no existe."""
    async with httpx.AsyncClient(base_url=BASE, timeout=10.0) as client:
        r = await client.get(f"/pokemon/{nombre_o_id.lower()}")
        r.raise_for_status()
        return r.json()