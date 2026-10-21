import polars as pl

from app.analysis.stats import compute_player_df


def build_player_summary(kills, damages, rounds, players, steamid: str) -> dict | None:
    df = compute_player_df(kills, damages, rounds, players)
    row = df.filter(pl.col("steamid").cast(pl.String) == steamid)
    if row.is_empty():
        return None  # le joueur connecté n'est pas dans cette démo

    p = row.row(0, named=True)
    return {
        "steamid": steamid,
        "name": p["name"],
        "rounds": rounds.height,
        "kills": p["kills"],
        "deaths": p["deaths"],
        "assists": p["assists"],
        "damage": int(p["damage"]),
        "adr": p["adr"],
        "hs_pct": p["hs_pct"],
    }


def _is_friendly(attacker_side: str, victim_side: str) -> pl.Expr:
    return (pl.col(attacker_side) == pl.col(victim_side)).fill_null(False)


def build_round_impact(kills, damages, rounds, players, steamid: str) -> dict | None:
    me_row = players.filter(pl.col("steamid").cast(pl.String) == steamid)
    if me_row.is_empty() or me_row["team"][0] is None:
        return None
    team = me_row["team"][0]

    def is_me(col: str) -> pl.Expr:
        return pl.col(col).cast(pl.String) == steamid

    k = (
        kills.filter(is_me("attacker_steamid") & ~_is_friendly("attacker_side", "victim_side"))
        .group_by("round_num")
        .agg(pl.len().alias("kills"), pl.col("headshot").sum().alias("headshots"))
    )
    d = (
        damages.filter(is_me("attacker_steamid") & ~_is_friendly("attacker_side", "victim_side"))
        .group_by("round_num")
        .agg(pl.col("dmg_health_real").sum().alias("damage"))
    )
    died = (
        kills.filter(is_me("victim_steamid"))
        .select("round_num")
        .unique()
        .with_columns(pl.lit(True).alias("died"))
    )

    # Même convention que build_teams : changement de côté après le round 12
    first_half = "ct" if team == 0 else "t"
    second_half = "t" if team == 0 else "ct"

    df = (
        rounds.select("round_num", "winner")
        .join(k, on="round_num", how="left")
        .join(d, on="round_num", how="left")
        .join(died, on="round_num", how="left")
        .with_columns(
            pl.col("kills", "headshots", "damage").fill_null(0),
            pl.col("died").fill_null(False),
            pl.when(pl.col("round_num") <= 12)
            .then(pl.lit(first_half))
            .otherwise(pl.lit(second_half))
            .alias("side"),
        )
        .with_columns((pl.col("winner").str.to_lowercase() == pl.col("side")).alias("won"))
        .select("round_num", "side", "won", "kills", "headshots", "damage", "died")
        .sort("round_num")
    )
    return {"rounds": df.to_dicts()}

def build_kill_timing(kills, rounds, players, steamid: str, tickrate: float) -> dict | None:
    me_row = players.filter(pl.col("steamid").cast(pl.String) == steamid)
    if me_row.is_empty() or me_row["team"][0] is None:
        return None
    team = me_row["team"][0]

    def is_me(col: str) -> pl.Expr:
        return pl.col(col).cast(pl.String) == steamid

    # ADAPTER : "freeze_end" est le tick de début du jeu actif (colonne d'awpy 2.x)
    starts = rounds.select("round_num", pl.col("freeze_end").alias("round_start"))

    def events(condition: pl.Expr, kind: str) -> pl.DataFrame:
        return (
            kills.filter(condition)
            .join(starts, on="round_num")
            .select(
                "round_num",
                pl.lit(kind).alias("kind"),
                ((pl.col("tick") - pl.col("round_start")) / tickrate)
                .clip(lower_bound=0)
                .round(1)
                .alias("seconds"),
            )
        )

    kill_ev = events(
        is_me("attacker_steamid") & ~_is_friendly("attacker_side", "victim_side"), "kill"
    )
    death_ev = events(is_me("victim_steamid"), "death")

    first_half = "ct" if team == 0 else "t"
    second_half = "t" if team == 0 else "ct"

    df = (
        pl.concat([kill_ev, death_ev])
        .with_columns(
            pl.when(pl.col("round_num") <= 12)
            .then(pl.lit(first_half))
            .otherwise(pl.lit(second_half))
            .alias("side")
        )
        .select("round_num", "side", "kind", "seconds")
        .sort("round_num", "seconds")
    )
    return {"events": df.to_dicts()}