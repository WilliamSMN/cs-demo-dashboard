from typing import Literal

from pydantic import BaseModel


class MatchMeta(BaseModel):
    id: str
    filename: str | None = None
    status: Literal["processing", "ready", "failed"]
    map_name: str | None = None
    tickrate: float | None = None
    rounds: int | None = None
    error: str | None = None


class PlayerStats(BaseModel):
    steamid: str  # chaîne : un SteamID64 dépasse la précision des nombres JavaScript
    name: str
    kills: int
    deaths: int
    assists: int
    adr: float
    hs_pct: float


class StatsResponse(BaseModel):
    players: list[PlayerStats]
    unattributed_deaths: int