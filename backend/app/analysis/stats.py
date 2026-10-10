import polars as pl


def compute_player_stats(
    kills: pl.DataFrame,
    damages: pl.DataFrame,
    rounds: pl.DataFrame,
    players: pl.DataFrame,
) -> pl.DataFrame:
    """Une ligne par joueur : kills, deaths, assists, adr, hs_pct.

    Les événements dont la victime n'est pas identifiée (camp nul) sont comptés
    comme des événements adverses : seuls les tirs amis explicitement
    identifiés (camps connus et identiques) sont écartés.
    Les morts sans victime identifiée ne peuvent être attribuées à personne,
    donc deaths est sous-estimé d'autant.
    """
    n_rounds = rounds.height

    def is_friendly(attacker_side: str, victim_side: str) -> pl.Expr:
        return (pl.col(attacker_side) == pl.col(victim_side)).fill_null(False)

    enemy_kills = kills.filter(
        pl.col("attacker_steamid").is_not_null()
        & ~is_friendly("attacker_side", "victim_side")
    )
    enemy_assists = kills.filter(
        pl.col("assister_steamid").is_not_null()
        & ~is_friendly("assister_side", "victim_side")
    )
    enemy_damage = damages.filter(
        pl.col("attacker_steamid").is_not_null()
        & ~is_friendly("attacker_side", "victim_side")
    )

    k = enemy_kills.group_by(pl.col("attacker_steamid").alias("steamid")).agg(
        pl.len().alias("kills"),
        pl.col("headshot").sum().alias("headshots"),
    )
    d = (
        kills.filter(pl.col("victim_steamid").is_not_null())
        .group_by(pl.col("victim_steamid").alias("steamid"))
        .agg(pl.len().alias("deaths"))
    )
    a = enemy_assists.group_by(pl.col("assister_steamid").alias("steamid")).agg(
        pl.len().alias("assists")
    )
    dmg = enemy_damage.group_by(pl.col("attacker_steamid").alias("steamid")).agg(
        pl.col("dmg_health_real").sum().alias("damage")
    )

    counts = ["kills", "headshots", "deaths", "assists", "damage"]
    return (
        players.join(k, on="steamid", how="left")
        .join(d, on="steamid", how="left")
        .join(a, on="steamid", how="left")
        .join(dmg, on="steamid", how="left")
        .with_columns(pl.col(counts).fill_null(0))
        .with_columns(
            (pl.col("damage") / n_rounds).alias("adr"),
            pl.when(pl.col("kills") > 0)
            .then(pl.col("headshots") / pl.col("kills"))
            .otherwise(0.0)
            .alias("hs_pct"),
        )
        .select("steamid", "name", "kills", "deaths", "assists", "adr", "hs_pct")
        .sort("kills", descending=True)
    )