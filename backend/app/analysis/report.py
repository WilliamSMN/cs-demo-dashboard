import polars as pl

from app.analysis.common import is_friendly, is_player, player_team, with_side
from app.analysis.stats import (
    compute_clutches,
    compute_player_df,
    compute_trade_stats,
    compute_utility_stats,
)


def _my_kills(kills: pl.DataFrame, steamid: str) -> pl.DataFrame:
    return kills.filter(
        is_player("attacker_steamid", steamid) & ~is_friendly("attacker_side", "victim_side")
    )


def _my_damage(damages: pl.DataFrame, steamid: str) -> pl.DataFrame:
    return damages.filter(
        is_player("attacker_steamid", steamid) & ~is_friendly("attacker_side", "victim_side")
    )


def build_player_summary(kills, damages, rounds, players, steamid: str) -> dict | None:
    df = compute_player_df(kills, damages, rounds, players)
    row = df.filter(is_player("steamid", steamid))
    if row.is_empty():
        return None  # le joueur connecté n'est pas dans cette démo

    p = row.row(0, named=True)
    return {
        "steamid": steamid,
        "name": p["name"],
        "team": p["team"],
        "rounds": rounds.height,
        "kills": p["kills"],
        "deaths": p["deaths"],
        "assists": p["assists"],
        "damage": int(p["damage"]),
        "adr": p["adr"],
        "hs_pct": p["hs_pct"],
    }


def build_round_impact(kills, damages, rounds, players, steamid: str) -> dict | None:
    team = player_team(players, steamid)
    if team is None:
        return None

    k = (
        _my_kills(kills, steamid)
        .group_by("round_num")
        .agg(pl.len().alias("kills"), pl.col("headshot").sum().alias("headshots"))
    )
    d = (
        _my_damage(damages, steamid)
        .group_by("round_num")
        .agg(pl.col("dmg_health_real").sum().alias("damage"))
    )
    died = (
        kills.filter(is_player("victim_steamid", steamid))
        .select("round_num")
        .unique()
        .with_columns(pl.lit(True).alias("died"))
    )

    df = (
        rounds.select("round_num", "winner")
        .join(k, on="round_num", how="left")
        .join(d, on="round_num", how="left")
        .join(died, on="round_num", how="left")
        .with_columns(
            pl.col("kills", "headshots", "damage").fill_null(0),
            pl.col("died").fill_null(False),
        )
    )
    df = with_side(df, team).with_columns(
        (pl.col("winner").str.to_lowercase() == pl.col("side")).alias("won")
    )
    df = df.select("round_num", "side", "won", "kills", "headshots", "damage", "died")
    return {"rounds": df.sort("round_num").to_dicts()}


def build_kill_timing(kills, rounds, players, steamid: str, tickrate: float) -> dict | None:
    team = player_team(players, steamid)
    if team is None:
        return None

    # ADAPTER : "freeze_end" est le tick de début du jeu actif (colonne d'awpy 2.x)
    starts = rounds.select("round_num", pl.col("freeze_end").alias("round_start"))

    def events(source: pl.DataFrame, kind: str) -> pl.DataFrame:
        return source.join(starts, on="round_num").select(
            "round_num",
            pl.lit(kind).alias("kind"),
            ((pl.col("tick") - pl.col("round_start")) / tickrate)
            .clip(lower_bound=0)
            .round(1)
            .alias("seconds"),
        )

    all_events = pl.concat([
        events(_my_kills(kills, steamid), "kill"),
        events(kills.filter(is_player("victim_steamid", steamid)), "death"),
    ])
    df = with_side(all_events, team).select("round_num", "side", "kind", "seconds")
    return {"events": df.sort("round_num", "seconds").to_dicts()}


def build_opening_duels(kills, players, steamid: str) -> dict | None:
    team = player_team(players, steamid)
    if team is None:
        return None

    # Premier kill ennemi de chaque round (victime identifiée)
    first_kills = (
        kills.filter(
            pl.col("attacker_steamid").is_not_null()
            & pl.col("victim_steamid").is_not_null()
            & ~is_friendly("attacker_side", "victim_side")
        )
        .sort("tick")
        .unique(subset="round_num", keep="first", maintain_order=True)
    )
    mine = first_kills.filter(
        is_player("attacker_steamid", steamid) | is_player("victim_steamid", steamid)
    ).select("round_num", is_player("attacker_steamid", steamid).alias("won"))

    df = with_side(mine, team).select("round_num", "side", "won")
    return {"duels": df.sort("round_num").to_dicts()}


def _find_player(result: dict, steamid: str) -> dict | None:
    for team in result["teams"]:
        for p in team["players"]:
            if p["steamid"] == steamid:  # build_teams a déjà converti steamid en str
                return p
    return None


def build_extras(
    kills, damages, flashes, flash_throws, rounds, players, steamid: str, tickrate: float
) -> dict | None:
    trade_p = _find_player(compute_trade_stats(kills, players, rounds, tickrate), steamid)
    util_p = _find_player(
        compute_utility_stats(kills, damages, flashes, flash_throws, players, rounds), steamid
    )
    if trade_p is None or util_p is None:
        return None

    clutches = (
        compute_clutches(kills, players, rounds)
        .filter(is_player("steamid", steamid))
        .sort("round_num")
        .select("round_num", "vs", "won")
    )
    return {
        "trades": {k: trade_p[k] for k in ("trade_kills", "traded_deaths", "untraded_deaths")},
        "utility": {
            k: util_p[k]
            for k in (
                "flashes_thrown", "enemies_flashed", "team_flashed",
                "flash_assists", "he_damage", "molotov_damage", "blind_time",
            )
        },
        "clutches": clutches.to_dicts(),
    }