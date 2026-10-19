import logging
from pathlib import Path

import polars as pl
from awpy import Demo

from app.services import store

logger = logging.getLogger(__name__)


def ingest_demo(match_id: str, demo_path: Path) -> None:
    """Parse la démo une fois, sauvegarde les tables utiles en Parquet."""
    try:
        dem = Demo(demo_path)
        dem.parse(events=[
            *dem.default_events,
            "player_blind",
        ])

        folder = store.match_dir(match_id)
        folder.mkdir(parents=True, exist_ok=True)
        dem.kills.write_parquet(folder / "kills.parquet")
        dem.damages.write_parquet(folder / "damages.parquet")
        dem.rounds.write_parquet(folder / "rounds.parquet")
        players = (
            dem.ticks
            .filter(
                pl.col("steamid").is_not_null()
                & pl.col("side").is_not_null()
            )
            .sort("tick")
            .group_by("steamid")
            .agg(
                pl.col("name").drop_nulls().last().alias("name"),
                pl.col("side").first().alias("starting_side"),
            )
            .with_columns(
                pl.when(pl.col("starting_side").str.to_lowercase() == "ct")
                .then(pl.lit(0))
                .when(pl.col("starting_side").str.to_lowercase() == "t")
                .then(pl.lit(1))
                .otherwise(pl.lit(None, dtype=pl.Int64))
                .alias("team")
            )
            .drop("starting_side")
        )
        players.write_parquet(folder / "players.parquet")

        blinds = dem.events["player_blind"].select(
            pl.col("attacker_steamid"),
            pl.col("user_steamid").alias("victim_steamid"),
            pl.col("blind_duration"),
        )
        blinds.write_parquet(folder / "flashes.parquet")

        throws = (
            dem.events["flashbang_detonate"]
            .filter(pl.col("user_steamid").is_not_null())
            .group_by(pl.col("user_steamid").alias("steamid"))
            .agg(pl.len().alias("flashes_thrown"))
        )
        throws.write_parquet(folder / "flash_throws.parquet")

        store.update_meta(
            match_id,
            status="ready",
            map_name=dem.header.get("map_name"),
            tickrate=dem.tickrate,
            rounds=dem.rounds.height,
        )
    except Exception as exc:
        logger.exception("Echec du parsing du match %s", match_id)
        store.update_meta(match_id, status="failed", error=str(exc))