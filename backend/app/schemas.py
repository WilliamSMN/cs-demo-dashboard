from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")
Side = Literal["ct", "t"]


class MatchMeta(BaseModel):
    id: str
    filename: str | None = None
    status: Literal["processing", "ready", "failed"]
    map_name: str | None = None
    tickrate: float | None = None
    rounds: int | None = None
    error: str | None = None


# Enveloppe commune : une équipe contient des joueurs d'un type donné
class Team(BaseModel, Generic[T]):
    name: str
    score: int
    players: list[T]


class Teams(BaseModel, Generic[T]):
    teams: list[Team[T]]


# Identité commune à tous les joueurs
class PlayerBase(BaseModel):
    steamid: str
    name: str
    team: int | None = None


# Compteurs par domaine (réutilisés dans le Player report)
class TradeCounts(BaseModel):
    trade_kills: int
    traded_deaths: int
    untraded_deaths: int


class UtilityCounts(BaseModel):
    flashes_thrown: int
    enemies_flashed: int
    team_flashed: int
    flash_assists: int
    he_damage: int
    molotov_damage: int
    blind_time: float


# Page General
class PlayerStats(PlayerBase):
    kills: int
    deaths: int
    assists: int
    damage: int
    adr: float
    hs_pct: float


class PlayerTrades(PlayerBase, TradeCounts):
    pass


class PlayerUtility(PlayerBase, UtilityCounts):
    pass


class PlayerClutch(PlayerBase):
    clutch_won: int
    clutch_total: int


class StatsResponse(Teams[PlayerStats]):
    unattributed_deaths: int


class TradesResponse(Teams[PlayerTrades]):
    pass


class UtilityResponse(Teams[PlayerUtility]):
    pass


class ClutchResponse(Teams[PlayerClutch]):
    pass


# Player report
class PlayerReportSummary(PlayerStats):
    rounds: int
    kast: float | None = None
    rating: float | None = None


class RoundImpact(BaseModel):
    round_num: int
    side: Side
    won: bool
    kills: int
    headshots: int
    damage: int
    died: bool


class RoundImpactResponse(BaseModel):
    rounds: list[RoundImpact]


class KillEvent(BaseModel):
    round_num: int
    side: Side
    kind: Literal["kill", "death"]
    seconds: float


class KillTimingResponse(BaseModel):
    events: list[KillEvent]


class OpeningDuel(BaseModel):
    round_num: int
    side: Side
    won: bool


class OpeningDuelsResponse(BaseModel):
    duels: list[OpeningDuel]


class ClutchRound(BaseModel):
    round_num: int
    vs: int
    won: bool


class ExtrasResponse(BaseModel):
    trades: TradeCounts
    utility: UtilityCounts
    clutches: list[ClutchRound]