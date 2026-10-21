import json
from functools import lru_cache
from pathlib import Path

import polars as pl

# backend/assets/maps (ce fichier est dans backend/app/analysis)
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "maps"
RADAR_SIZE = 1024


@lru_cache
def _map_data() -> dict:
    path = ASSETS_DIR / "map_data.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def radar_path(map_name: str) -> Path | None:
    path = ASSETS_DIR / f"{map_name}.png"
    return path if path.is_file() else None


def radar_exprs(map_name: str | None) -> list[pl.Expr]:
    """Expressions px, py (pixels de l'image radar) à partir des colonnes x, y du jeu."""
    d = _map_data().get(map_name or "")
    if d is None:  # carte inconnue : pas de conversion possible
        return [
            pl.lit(None, dtype=pl.Float64).alias("px"),
            pl.lit(None, dtype=pl.Float64).alias("py"),
        ]
    return [
        ((pl.col("x") - d["pos_x"]) / d["scale"]).alias("px"),
        ((d["pos_y"] - pl.col("y")) / d["scale"]).alias("py"),
    ]