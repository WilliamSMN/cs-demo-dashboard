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
        dem.parse()

        folder = store.match_dir(match_id)
        folder.mkdir(parents=True, exist_ok=True)
        dem.kills.write_parquet(folder / "kills.parquet")
        dem.damages.write_parquet(folder / "damages.parquet")
        dem.rounds.write_parquet(folder / "rounds.parquet")
        players = dem.ticks.group_by("steamid").agg(pl.col("name").last())
        players.write_parquet(folder / "players.parquet")

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