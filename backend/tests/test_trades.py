import polars as pl

from app.analysis.trades import compute_trades

A, B, X = 1, 2, 10  # A et B en CT, X en T


def make_kills(rows):
    return pl.DataFrame(
        rows,
        schema=["round_num", "tick", "attacker_steamid", "attacker_side",
                "victim_steamid", "victim_name", "victim_side"],
        orient="row",
    )


def is_traded(df, victim):
    return df.filter(pl.col("victim_steamid") == victim)["traded"][0]


def test_trade_within_window():
    kills = make_kills([
        (1, 100, X, "t", A, "A", "ct"),
        (1, 228, B, "ct", X, "X", "t"),   # 128 ticks = 1 s à 128 tick/s
    ])
    assert is_traded(compute_trades(kills, tickrate=128), A)


def test_revenge_too_late():
    kills = make_kills([
        (1, 100, X, "t", A, "A", "ct"),
        (1, 740, B, "ct", X, "X", "t"),   # 5 s
    ])
    assert not is_traded(compute_trades(kills, tickrate=128), A)


def test_victim_cannot_trade_himself():
    # Cas du round 3 : la kill de "vengeance" est attribuée à la victime (ex. molotov)
    kills = make_kills([
        (1, 100, X, "t", A, "A", "ct"),
        (1, 164, A, "ct", X, "X", "t"),
    ])
    assert not is_traded(compute_trades(kills, tickrate=128), A)


def test_tickrate_changes_the_delay():
    kills = make_kills([
        (1, 100, X, "t", A, "A", "ct"),
        (1, 356, B, "ct", X, "X", "t"),   # 256 ticks
    ])
    assert is_traded(compute_trades(kills, tickrate=128), A)       # 2 s
    assert not is_traded(compute_trades(kills, tickrate=64), A)    # 4 s