import time

import httpx

from app.config import settings

SUMMARIES_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
_TTL_S = 3600
_cache: dict[str, tuple[float, dict | None]] = {}


async def get_steam_profile(steamid: str) -> dict | None:
    cached = _cache.get(steamid)
    if cached and time.monotonic() - cached[0] < _TTL_S:
        return cached[1]

    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(
            SUMMARIES_URL,
            params={"key": settings.steam_api_key, "steamids": steamid},
        )
    resp.raise_for_status()

    players = resp.json()["response"]["players"]
    profile = None
    if players:
        p = players[0]
        profile = {
            "steamid": p["steamid"],
            "name": p.get("personaname"),
            "avatar": p.get("avatarfull"),
            "is_public": p.get("communityvisibilitystate") == 3,
        }
    _cache[steamid] = (time.monotonic(), profile)
    return profile