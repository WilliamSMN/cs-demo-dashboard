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

class PlayerTrades(BaseModel):
    steamid: str
    name: str
    team: int | None
    trade_kills: int
    traded_deaths: int
    untraded_deaths: int

class TradeTeam(BaseModel):
    name: str
    score: int
    players: list[PlayerTrades]

class TradesResponse(BaseModel):
    teams: list[TradeTeam]

class PlayerUtility(BaseModel):
    steamid: str
    name: str
    team: int | None
    enemies_flashed: int
    team_flashed: int
    flash_assists: int
    he_damage: int
    molotov_damage: int
    blind_time: float
    flashes_thrown: int

class UtilityTeam(BaseModel):
    name: str
    score: int
    players: list[PlayerUtility]

class UtilityResponse(BaseModel):
    teams: list[UtilityTeam]


class PlayerClutch(BaseModel):
    steamid: str
    name: str
    team: int | None
    clutch_won: int
    clutch_total: int

class ClutchTeam(BaseModel):
    name: str
    score: int
    players: list[PlayerClutch]

class ClutchResponse(BaseModel):
    teams: list[ClutchTeam]