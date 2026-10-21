import polars as pl

HALF_LENGTH = 12

def is_friendly(attacker_side: str, victim_side: str) -> pl.Expr:
    return (pl.col(attacker_side) == pl.col(victim_side)).fill_null(False)


def is_player(col: str, steamid: str) -> pl.Expr:
    return pl.col(col).cast(pl.String) == steamid


def player_team(players: pl.DataFrame, steamid: str) -> int | None:
    """Équipe de départ (0 = CT, 1 = T), ou None si le joueur est absent ou sans équipe."""
    row = players.filter(is_player("steamid", steamid))
    return None if row.is_empty() else row["team"][0]


def with_side(df: pl.DataFrame, team: int) -> pl.DataFrame:
    """Ajoute la colonne 'side' ('ct' ou 't') du joueur pour chaque round_num."""
    first_half = "ct" if team == 0 else "t"
    second_half = "t" if team == 0 else "ct"
    return df.with_columns(
        pl.when(pl.col("round_num") <= HALF_LENGTH)
        .then(pl.lit(first_half))
        .otherwise(pl.lit(second_half))
        .alias("side")
    )


def merge_player_tables(
    players: pl.DataFrame,
    tables: list[pl.DataFrame],
    counts: list[str],
    sort_by: str,
    floats: tuple[str, ...] = (),
) -> pl.DataFrame:
    """Joint des agrégats par steamid aux joueurs, remplit les trous par 0 et trie."""
    df = players
    for table in tables:
        df = df.join(table, on="steamid", how="left")
    return (
        df.with_columns(
            pl.col(counts).fill_null(0),
            *(pl.col(f).fill_null(0.0) for f in floats),
        )
        .select("steamid", "name", "team", *counts, *floats)
        .sort(sort_by, descending=True)
    )