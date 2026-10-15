import polars as pl

from app.analysis.stats import compute_player_stats

A, B, X = 1, 2, 10  # A et B en CT, X en T

KILL_SCHEMA = {
    "round_num": pl.UInt32, "tick": pl.Int64,
    "attacker_steamid": pl.Int64, "attacker_side": pl.String,
    "victim_steamid": pl.Int64, "victim_name": pl.String, "victim_side": pl.String,
    "assister_steamid": pl.Int64, "assister_side": pl.String,
    "headshot": pl.Boolean,
}
DAMAGE_SCHEMA = {
    "round_num": pl.UInt32, "attacker_steamid": pl.Int64,
    "attacker_side": pl.String, "victim_side": pl.String,
    "dmg_health_real": pl.Int64,
}


def build_stats():
    kills = pl.DataFrame(
        [
            (1, 100, X, "t", A, "A", "ct", None, None, True),
            (1, 228, B, "ct", X, "X", "t", None, None, False),
            (2, 500, X, "t", B, "B", "ct", None, None, False),
        ],
        schema=KILL_SCHEMA, orient="row",
    )
    damages = pl.DataFrame(
        [
            (1, B, "ct", "t", 100),
            (1, X, "t", "ct", 100),
            (2, X, "t", "ct", 100),
        ],
        schema=DAMAGE_SCHEMA, orient="row",
    )
    rounds = pl.DataFrame(
        {
            "round_num": [1, 2],
            "ct_score": [0, 1],
            "t_score": [1, 1],
        },
        schema={
            "round_num": pl.UInt32,
            "ct_score": pl.Int64,
            "t_score": pl.Int64,
        },
    )
    players = pl.DataFrame(
        {"steamid": [A, B, X], "name": ["A", "B", "X"], "team": [0, 0, 1]},
        schema={"steamid": pl.Int64, "name": pl.String, "team": pl.Int64},
    )
    return compute_player_stats(kills, damages, rounds, players)

def row(stats_result: dict, steamid: int) -> dict:
    """Aplatit les joueurs de toutes les équipes pour les tests unitaires."""
    all_players = [p for team in stats_result["teams"] for p in team["players"]]
    return next(p for p in all_players if p["steamid"] == str(steamid))


def test_counts_and_adr():
    stats = build_stats()
    assert row(stats, X)["kills"] == 2
    assert row(stats, B)["deaths"] == 1
    assert row(stats, X)["adr"] == 100
    assert row(stats, B)["adr"] == 50
    assert row(stats, A)["adr"] == 0


def test_headshot_ratio():
    stats = build_stats()
    assert row(stats, X)["hs_pct"] == 0.5  # 1 headshot sur 2 kills


def test_kill_with_unidentified_victim_is_counted():
    kills = pl.DataFrame(
        [(1, 100, X, "t", None, None, None, None, None, False)],
        schema=KILL_SCHEMA, orient="row",
    )
    damages = pl.DataFrame([], schema=DAMAGE_SCHEMA)
    
    # Ajout des colonnes de score requises par le code
    rounds = pl.DataFrame(
        {"round_num": [1], "ct_score": [0], "t_score": [0]},
        schema={"round_num": pl.UInt32, "ct_score": pl.Int64, "t_score": pl.Int64}
    )
    
    players = pl.DataFrame(
        {"steamid": [A, X], "name": ["A", "X"], "team": [0, 1]},
        schema={"steamid": pl.Int64, "name": pl.String, "team": pl.Int64},
    )
    stats = compute_player_stats(kills, damages, rounds, players)
    assert row(stats, X)["kills"] == 1