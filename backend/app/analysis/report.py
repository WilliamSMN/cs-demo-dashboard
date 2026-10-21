import polars as pl

from app.analysis.common import is_friendly, is_player, player_team, with_side
from app.analysis.stats import (
    compute_clutches,
    compute_player_df,
    compute_trade_stats,
    compute_trades,
    compute_utility_stats,
)
from app.analysis.radar import radar_exprs

def _my_kills(kills: pl.DataFrame, steamid: str) -> pl.DataFrame:
    return kills.filter(
        is_player("attacker_steamid", steamid) & ~is_friendly("attacker_side", "victim_side")
    )


def _my_damage(damages: pl.DataFrame, steamid: str) -> pl.DataFrame:
    return damages.filter(
        is_player("attacker_steamid", steamid) & ~is_friendly("attacker_side", "victim_side")
    )


def _my_assists(kills: pl.DataFrame, steamid: str) -> pl.DataFrame:
    return kills.filter(
        is_player("assister_steamid", steamid) & ~is_friendly("assister_side", "victim_side")
    )


def _kast(table: pl.DataFrame, trades: pl.DataFrame, steamid: str) -> float:
    # ADAPTER : on suppose que compute_trades renvoie round_num, victim_steamid et traded
    traded_rounds = trades.filter(
        is_player("victim_steamid", steamid) & pl.col("traded")
    )["round_num"].to_list()
    hit = table.filter(
        (pl.col("kills") > 0)
        | (pl.col("assists") > 0)
        | ~pl.col("died")
        | pl.col("round_num").is_in(traded_rounds)
    )
    return hit.height / table.height


def _rating(kast: float, kills: int, deaths: int, assists: int, adr: float, rounds: int) -> float:
    kpr, dpr, apr = kills / rounds, deaths / rounds, assists / rounds
    impact = 2.13 * kpr + 0.42 * apr - 0.41
    return (
        0.0073 * (kast * 100)
        + 0.3591 * kpr
        - 0.5329 * dpr
        + 0.2372 * impact
        + 0.0032 * adr
        + 0.1587
    )


def build_player_summary(
    kills, damages, rounds, players, steamid: str, tickrate: float
) -> dict | None:
    df = compute_player_df(kills, damages, rounds, players)
    row = df.filter(is_player("steamid", steamid))
    if row.is_empty():
        return None  # le joueur connecté n'est pas dans cette démo

    p = row.row(0, named=True)
    n_rounds = rounds.height

    table = _round_table(kills, damages, rounds, players, steamid)
    kast = rating = None
    if table is not None and n_rounds:
        kast = _kast(table, compute_trades(kills, tickrate), steamid)
        rating = _rating(kast, p["kills"], p["deaths"], p["assists"], p["adr"], n_rounds)

    return {
        "steamid": steamid,
        "name": p["name"],
        "team": p["team"],
        "rounds": n_rounds,
        "kills": p["kills"],
        "deaths": p["deaths"],
        "assists": p["assists"],
        "damage": int(p["damage"]),
        "adr": p["adr"],
        "hs_pct": p["hs_pct"],
        "kast": None if kast is None else round(kast, 3),
        "rating": None if rating is None else round(rating, 2),
    }


def _round_table(kills, damages, rounds, players, steamid: str) -> pl.DataFrame | None:
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
    a = _my_assists(kills, steamid).group_by("round_num").agg(pl.len().alias("assists"))
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
        .join(a, on="round_num", how="left")
        .join(died, on="round_num", how="left")
        .with_columns(
            pl.col("kills", "headshots", "damage", "assists").fill_null(0),
            pl.col("died").fill_null(False),
        )
    )
    return (
        with_side(df, team)
        .with_columns((pl.col("winner").str.to_lowercase() == pl.col("side")).alias("won"))
        .sort("round_num")
    )


def build_round_impact(kills, damages, rounds, players, steamid: str) -> dict | None:
    table = _round_table(kills, damages, rounds, players, steamid)
    if table is None:
        return None
    cols = ["round_num", "side", "won", "kills", "headshots", "damage", "died"]
    return {"rounds": table.select(cols).to_dicts()}


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


_HURT_ALIASES = {"m4a1": "m4a1_silencer", "hkp2000": "usp_silencer"}


def _align_damage_weapons(my_damage: pl.DataFrame, my_kills: pl.DataFrame) -> pl.DataFrame:
    """Renomme les dégâts quand le joueur n'a des kills qu'avec la variante silencieuse."""
    used = set(my_kills["weapon"].unique())
    mapping = {h: k for h, k in _HURT_ALIASES.items() if k in used and h not in used}
    return my_damage.with_columns(pl.col("weapon").replace(mapping)) if mapping else my_damage


def build_weapons_and_opponents(kills, damages, steamid: str) -> dict:
    my_kills = _my_kills(kills, steamid)

    # Armes : kills et headshots, puis dégâts, joints par arme
    by_kills = my_kills.group_by("weapon").agg(
        pl.len().alias("kills"),
        pl.col("headshot").sum().alias("headshots"),
    )
    by_damage = (
        _align_damage_weapons(_my_damage(damages, steamid), my_kills)
        .group_by("weapon")
        .agg(pl.col("dmg_health_real").sum().alias("damage"))
    )
    weapons = (
        by_kills.join(by_damage, on="weapon", how="full", coalesce=True)
        .with_columns(pl.col("kills", "headshots", "damage").fill_null(0))
        .sort("kills", "damage", descending=True)
    )

    # Adversaires : qui j'ai tué, qui m'a tué
    killed = (
        my_kills.filter(pl.col("victim_steamid").is_not_null())
        .group_by(pl.col("victim_steamid").alias("steamid"))
        .agg(pl.col("victim_name").last().alias("name"), pl.len().alias("killed"))
    )
    killed_by = (
        kills.filter(
            is_player("victim_steamid", steamid)
            & pl.col("attacker_steamid").is_not_null()
            & ~is_friendly("attacker_side", "victim_side")
        )
        .group_by(pl.col("attacker_steamid").alias("steamid"))
        .agg(pl.col("attacker_name").last().alias("name_b"), pl.len().alias("killed_by"))
    )
    opponents = (
        killed.join(killed_by, on="steamid", how="full", coalesce=True)
        .with_columns(
            pl.coalesce("name", "name_b").alias("name"),
            pl.col("killed", "killed_by").fill_null(0),
            pl.col("steamid").cast(pl.String),
        )
        .select("steamid", "name", "killed", "killed_by")
        .sort("killed", "killed_by", descending=True)
    )

    return {"weapons": weapons.to_dicts(), "opponents": opponents.to_dicts()}


def build_positions(kills, players, steamid: str, map_name: str | None) -> dict | None:
    team = player_team(players, steamid)
    if team is None:
        return None

    def events(source: pl.DataFrame, kind: str, prefix: str) -> pl.DataFrame:
        return source.filter(pl.col(f"{prefix}_X").is_not_null()).select(
            "round_num",
            pl.lit(kind).alias("kind"),
            pl.col(f"{prefix}_X").alias("x"),
            pl.col(f"{prefix}_Y").alias("y"),
            pl.col(f"{prefix}_Z").alias("z"),
        )

    all_events = pl.concat([
        events(_my_kills(kills, steamid), "kill", "attacker"),
        events(kills.filter(is_player("victim_steamid", steamid)), "death", "victim"),
    ])
    df = (
        with_side(all_events, team)
        .with_columns(*radar_exprs(map_name))
        .select("round_num", "side", "kind", "x", "y", "z", "px", "py")
    )
    return {"events": df.sort("round_num").to_dicts()}