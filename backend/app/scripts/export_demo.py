"""Exporte les réponses du rapport en JSON statiques pour la démo publique.

Usage (depuis backend/) :
    uv run python scripts/export_demo.py [dossier_demo] [dossier_sortie]
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import polars as pl  # noqa: E402

from app.analysis.profile import build_profile
from app.analysis.radar import radar_path
from app.analysis.report import (
    build_extras,
    build_kill_timing,
    build_opening_duels,
    build_player_summary,
    build_positions,
    build_round_impact,
    build_weapons_and_opponents,
)
from app.schemas import (
    ExtrasResponse,
    KillTimingResponse,
    OpeningDuelsResponse,
    PlayerReportSummary,
    PositionsResponse,
    ProfileResponse,
    RoundImpactResponse,
    WeaponsResponse,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=Path("demo_data/de0de0de0de0"))
    parser.add_argument("dest", type=Path, nargs="?", default=Path("../frontend/public/demo"))
    args = parser.parse_args()

    meta = json.loads((args.source / "meta.json").read_text(encoding="utf-8"))
    owner = str(meta["owner"])
    tickrate = meta.get("tickrate") or 64
    map_name = meta.get("map_name")

    names = ("kills", "damages", "rounds", "players", "flashes", "flash_throws")
    t = {n: pl.read_parquet(args.source / f"{n}.parquet") for n in names}
    k, d, r, p = t["kills"], t["damages"], t["rounds"], t["players"]
    f, ft = t["flashes"], t["flash_throws"]

    positions = build_positions(k, p, owner, map_name)
    outputs = {
        "summary": (PlayerReportSummary, build_player_summary(k, d, r, p, owner, tickrate)),
        "rounds": (RoundImpactResponse, build_round_impact(k, d, r, p, owner)),
        "timing": (KillTimingResponse, build_kill_timing(k, r, p, owner, tickrate)),
        "opening": (OpeningDuelsResponse, build_opening_duels(k, p, owner)),
        "extras": (ExtrasResponse, build_extras(k, d, f, ft, r, p, owner, tickrate)),
        "weapons": (WeaponsResponse, build_weapons_and_opponents(k, d, owner)),
        "positions": (
            PositionsResponse,
            None if positions is None else {"map_name": map_name, **positions},
        ),
        "profile": (ProfileResponse, build_profile(k, d, f, ft, r, p, owner, tickrate)),
    }

    report_dir = args.dest / "report"
    report_dir.mkdir(parents=True, exist_ok=True)

    for name, (model, data) in outputs.items():
        if data is None:
            sys.exit(f"{name}: le joueur {owner} est introuvable dans cette démo.")
        payload = model(**data).model_dump(mode="json")  # même forme que l'API
        path = report_dir / f"{name}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{path}  ({path.stat().st_size} octets)")

    radar = radar_path(map_name or "")
    if radar is None:
        print(f"Attention : pas d'image radar pour {map_name}, elle ne sera pas copiée.")
    else:
        shutil.copyfile(radar, args.dest / "radar.png")
        print(f"{args.dest / 'radar.png'}")


if __name__ == "__main__":
    main()