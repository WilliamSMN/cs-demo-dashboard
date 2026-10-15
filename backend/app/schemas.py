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
    steamid: str
    name: str
    team: int | None = None
    kills: int
    deaths: int
    assists: int
    damage: int  # Corrigé en 'damage' (cohérent avec ton code précédent)
    adr: float
    hs_pct: float

class TeamStats(BaseModel):
    name: str        # Ex: "Team 0" (ou le nom réel si disponible)
    score: int       # Score final de l'équipe
    players: list[PlayerStats]

class StatsResponse(BaseModel):
    teams: list[TeamStats]
    unattributed_deaths: int