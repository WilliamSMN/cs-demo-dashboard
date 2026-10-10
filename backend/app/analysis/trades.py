import polars as pl


def compute_trades(
    kills: pl.DataFrame, tickrate: float, window_s: float = 3.0
) -> pl.DataFrame:
    """Une ligne par mort causée par un adversaire.

    delay_s : délai (en secondes) avant que le tueur soit abattu par un
              autre joueur du camp de la victime, null s'il ne l'est pas.
    traded  : True si delay_s <= window_s.
    """
    deaths = (
        kills.filter(
            pl.col("attacker_steamid").is_not_null()
            & (pl.col("attacker_side") != pl.col("victim_side"))
        )
        .select(
            "round_num",
            pl.col("tick").alias("death_tick"),
            "victim_steamid",
            "victim_name",
            "victim_side",
            pl.col("attacker_steamid").alias("killer_steamid"),
        )
        .with_row_index("death_id")
    )

    revenges = kills.select(
        "round_num",
        pl.col("tick").alias("revenge_tick"),
        pl.col("victim_steamid").alias("killer_steamid"),
        pl.col("attacker_side").alias("revenger_side"),
        pl.col("attacker_steamid").alias("revenger_steamid"),
    )

    delays = (
        deaths.join(revenges, on=["round_num", "killer_steamid"])
        .filter(
            (pl.col("revenger_side") == pl.col("victim_side"))
            & (pl.col("revenger_steamid") != pl.col("victim_steamid"))
            & (pl.col("revenge_tick") >= pl.col("death_tick"))
        )
        .group_by("death_id")
        .agg(
            ((pl.col("revenge_tick") - pl.col("death_tick")).min() / tickrate)
            .alias("delay_s")
        )
    )

    return (
        deaths.join(delays, on="death_id", how="left")
        .with_columns((pl.col("delay_s") <= window_s).fill_null(False).alias("traded"))
        .drop("death_id")
        .sort("round_num", "death_tick")
    )