"""Anonymise un dossier de match (Parquet + meta.json) pour en faire une démo publique.

Usage (depuis backend/) :
    uv run python scripts/anonymize_demo.py <dossier_source> <dossier_destination>
"""

import argparse
import json
import sys
from pathlib import Path

import polars as pl

VIEWER_NAME = "You"
FAKE_ID_BASE = 1000  # identifiants fictifs : trop petits pour être de vrais steamid64


def is_id_column(name: str) -> bool:
    return name == "steamid" or name.endswith(("_steamid", "_xuid"))


def is_name_column(name: str) -> bool:
    return name == "name" or name.endswith("_name")


def build_aliases(players: pl.DataFrame, viewer: int) -> dict[int, dict]:
    viewer_team = players.filter(pl.col("steamid") == viewer)["team"][0]
    aliases: dict[int, dict] = {}
    teammates = opponents = 0
    for steamid, team in players.select("steamid", "team").iter_rows():
        if steamid == viewer:
            name = VIEWER_NAME
        elif team == viewer_team:
            teammates += 1
            name = f"Teammate {teammates}"
        else:
            opponents += 1
            name = f"Opponent {opponents}"
        aliases[steamid] = {"id": FAKE_ID_BASE + len(aliases) + 1, "name": name}
    return aliases


def anonymize(df: pl.DataFrame, aliases: dict[int, dict]) -> pl.DataFrame:
    id_map = {sid: a["id"] for sid, a in aliases.items()}
    name_map = {sid: a["name"] for sid, a in aliases.items()}

    exprs = []
    for col in df.columns:
        if is_id_column(col):
            exprs.append(
                pl.col(col)
                .replace_strict(id_map, default=None, return_dtype=df.schema[col])
                .alias(col)
            )
        elif is_name_column(col):
            # 'attacker_name' -> 'attacker_steamid', 'name' -> 'steamid'
            id_col = col[: -len("name")] + "steamid"
            if id_col in df.columns:
                exprs.append(
                    pl.col(id_col)
                    .replace_strict(name_map, default=None, return_dtype=pl.String)
                    .alias(col)
                )
            else:
                print(f"  attention : {col} sans colonne d'identifiant associée, mise à null")
                exprs.append(pl.lit(None, dtype=pl.String).alias(col))
    return df.with_columns(exprs) if exprs else df


def find_leaks(df: pl.DataFrame, ids: set[int], names: set[str]) -> list[str]:
    leaks = []
    for col, dtype in df.schema.items():
        if dtype == pl.String and is_name_column(col):
            if df[col].is_in(list(names)).any():
                leaks.append(col)
        elif dtype.is_integer() and df[col].is_in(list(ids)).any():
            leaks.append(col)
    return leaks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("dest", type=Path)
    args = parser.parse_args()

    meta = json.loads((args.source / "meta.json").read_text(encoding="utf-8"))
    viewer = int(meta["owner"])

    players = pl.read_parquet(args.source / "players.parquet")
    if players.filter(pl.col("steamid") == viewer).is_empty():
        sys.exit("Le propriétaire du match n'est pas dans players.parquet.")
    aliases = build_aliases(players, viewer)

    # Phase 1 : tout anonymiser en mémoire et vérifier, sans rien écrire
    original_ids = set(aliases)
    original_names: set[str] = set()
    results: dict[str, pl.DataFrame] = {}
    for path in sorted(args.source.glob("*.parquet")):
        df = pl.read_parquet(path)
        for col in df.columns:
            if is_name_column(col) and df.schema[col] == pl.String:
                original_names.update(df[col].drop_nulls().to_list())
        results[path.name] = anonymize(df, aliases)
        print(f"{path.name}: {df.height} lignes")

    new_meta = {
        **meta,
        "id": args.dest.name,
        "owner": str(aliases[viewer]["id"]),
        "filename": "demo.dem",
    }
    meta_text = json.dumps(new_meta, indent=2)

    problems = [f"{name}: {col}" for name, df in results.items()
                for col in find_leaks(df, original_ids, original_names)]
    problems += [f"meta.json: {x}" for x in original_ids | original_names if str(x) in meta_text]
    if problems:
        sys.exit("Fuite détectée, rien n'a été écrit :\n  " + "\n  ".join(problems))

    # Phase 2 : écriture
    args.dest.mkdir(parents=True, exist_ok=True)
    for name, df in results.items():
        df.write_parquet(args.dest / name)
    (args.dest / "meta.json").write_text(meta_text, encoding="utf-8")

    print("\nAucune fuite détectée. Joueurs :")
    for alias in aliases.values():
        print(f"  {alias['id']}  {alias['name']}")
    print(f"\nDémo écrite dans {args.dest}")


if __name__ == "__main__":
    main()