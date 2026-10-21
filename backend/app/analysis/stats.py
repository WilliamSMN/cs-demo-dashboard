import polars as pl
from app.analysis.trades import compute_trades 


def build_teams(player_df: pl.DataFrame, rounds: pl.DataFrame) -> list[dict]:
    if "winner" in rounds.columns and rounds.height > 0:
        rounds_evaluated = rounds.with_columns(
            pl.when(pl.col("round_num") <= 12)
            .then(
                pl.when(pl.col("winner").str.to_uppercase() == "CT").then(pl.lit(0))
                .otherwise(pl.lit(1))
            )
            .otherwise(
                pl.when(pl.col("winner").str.to_uppercase() == "T").then(pl.lit(0))
                .otherwise(pl.lit(1))
            )
            .alias("round_winner_team")
        )
        team_0_score = rounds_evaluated.filter(pl.col("round_winner_team") == 0).height
        team_1_score = rounds_evaluated.filter(pl.col("round_winner_team") == 1).height
    else:
        team_0_score, team_1_score = 0, 0

    all_players = player_df.with_columns(pl.col("steamid").cast(pl.String)).to_dicts()

    teams = [
        {"name": "Team 1", "score": team_0_score,
         "players": [p for p in all_players if p.get("team") == 0]},
        {"name": "Team 2", "score": team_1_score,
         "players": [p for p in all_players if p.get("team") == 1]},
    ]
    others = [p for p in all_players if p.get("team") not in (0, 1)]
    if others:
        teams.append({"name": "Spectateurs / Indéfinis", "score": 0, "players": others})
    return teams

def compute_player_df(kills, damages, rounds, players) -> pl.DataFrame:
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
    
    player_df = (
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
        .select("steamid", "name", "team", "kills", "deaths", "assists", "damage", "adr", "hs_pct")
        .sort("kills", descending=True)
    )
    
    return player_df

def compute_player_stats(
    kills: pl.DataFrame,
    damages: pl.DataFrame,
    rounds: pl.DataFrame,
    players: pl.DataFrame,
) -> dict:
    player_df = compute_player_df(kills, damages, rounds, players)
    return {
        "teams": build_teams(player_df, rounds),
        "unattributed_deaths": kills["victim_steamid"].null_count(),
    }

def compute_trade_stats(
    kills: pl.DataFrame, players: pl.DataFrame, rounds: pl.DataFrame, tickrate: float
) -> dict:
    trades = compute_trades(kills, tickrate)

    deaths = trades.group_by(pl.col("victim_steamid").alias("steamid")).agg(
        pl.col("traded").sum().alias("traded_deaths"),
        (~pl.col("traded")).sum().alias("untraded_deaths"),
    )
    trade_kills = (
        trades.filter(pl.col("traded"))
        .group_by(pl.col("trader_steamid").alias("steamid"))
        .agg(pl.len().alias("trade_kills"))
    )

    counts = ["trade_kills", "traded_deaths", "untraded_deaths"]
    player_df = (
        players.join(trade_kills, on="steamid", how="left")
        .join(deaths, on="steamid", how="left")
        .with_columns(pl.col(counts).fill_null(0))
        .select("steamid", "name", "team", *counts)
        .sort("trade_kills", descending=True)
    )
    return {"teams": build_teams(player_df, rounds)}

def compute_clutches(
    kills: pl.DataFrame, players: pl.DataFrame, rounds: pl.DataFrame
) -> pl.DataFrame:
    team_of = {
        sid: team
        for sid, team in players.select("steamid", "team").iter_rows()
        if team in (0, 1)
    }
    winners = {
        r: (w or "").upper()
        for r, w in rounds.select("round_num", "winner").iter_rows()
    }

    rows = []
    deaths = kills.filter(pl.col("victim_steamid").is_not_null()).sort("round_num", "tick")
    for (round_num,), rk in deaths.group_by("round_num", maintain_order=True):
        alive = {0: set(), 1: set()}
        for sid, team in team_of.items():
            alive[team].add(sid)

        started = {}  # team -> (steamid, vs)
        for victim in rk["victim_steamid"]:
            team = team_of.get(victim)
            if team is None:
                continue
            alive[team].discard(victim)
            for t in (0, 1):
                if t not in started and len(alive[t]) == 1 and len(alive[1 - t]) >= 1:
                    started[t] = (next(iter(alive[t])), len(alive[1 - t]))

        for t, (sid, vs) in started.items():
            side = "CT" if (t == 0) == (round_num <= 12) else "T"
            won = sid in alive[t] and winners.get(round_num) == side
            rows.append({"steamid": sid, "round_num": round_num, "vs": vs, "won": won})

    return pl.DataFrame(
        rows,
        schema={"steamid": players.schema["steamid"], "round_num": pl.Int64,
                "vs": pl.Int64, "won": pl.Boolean},
    )


def compute_clutch_stats(
    kills: pl.DataFrame, players: pl.DataFrame, rounds: pl.DataFrame
) -> dict:
    clutches = compute_clutches(kills, players, rounds)
    agg = clutches.group_by("steamid").agg(
        pl.len().alias("clutch_total"),
        pl.col("won").sum().alias("clutch_won"),
    )
    counts = ["clutch_won", "clutch_total"]
    player_df = (
        players.join(agg, on="steamid", how="left")
        .with_columns(pl.col(counts).fill_null(0))
        .select("steamid", "name", "team", *counts)
        .sort("clutch_won", descending=True)
    )
    return {"teams": build_teams(player_df, rounds)}

def compute_utility_stats(
    kills: pl.DataFrame,
    damages: pl.DataFrame,
    flashes: pl.DataFrame,
    throws: pl.DataFrame,
    players: pl.DataFrame,
    rounds: pl.DataFrame,
) -> dict:
    enemy_dmg = damages.filter(
        pl.col("attacker_steamid").is_not_null()
        & (pl.col("attacker_side") != pl.col("victim_side"))
    )

    def dmg_by(weapons: list[str], alias: str) -> pl.DataFrame:
        return (
            enemy_dmg.filter(pl.col("weapon").is_in(weapons))
            .group_by(pl.col("attacker_steamid").alias("steamid"))
            .agg(pl.col("dmg_health_real").sum().alias(alias))
        )

    he = dmg_by(["hegrenade"], "he_damage")
    molotov = dmg_by(["inferno", "molotov", "incgrenade"], "molotov_damage")

    flash_assists = (
        kills.filter(
            pl.col("assister_steamid").is_not_null()
            & pl.col("assistedflash")
            & (pl.col("assister_side") != pl.col("victim_side"))
        )
        .group_by(pl.col("assister_steamid").alias("steamid"))
        .agg(pl.len().alias("flash_assists"))
    )

    valid = (
    flashes
    .filter(pl.col("attacker_steamid").is_not_null())
    .join(
        players.select(
            pl.col("steamid").alias("attacker_steamid"),
            pl.col("team").alias("attacker_team"),
        ),
        on="attacker_steamid",
        how="left",
    )
    .join(
        players.select(
            pl.col("steamid").alias("victim_steamid"),
            pl.col("team").alias("victim_team"),
        ),
        on="victim_steamid",
        how="left",
    )
)

    is_enemy = (
        pl.col("attacker_team").is_not_null()
        & pl.col("victim_team").is_not_null()
        & (pl.col("attacker_team") != pl.col("victim_team"))
        )

    is_team = (
        pl.col("attacker_team").is_not_null()
        & (pl.col("attacker_team") == pl.col("victim_team"))
        & (pl.col("attacker_steamid") != pl.col("victim_steamid"))
        )

    flash_stats = valid.group_by(
        pl.col("attacker_steamid").alias("steamid")
        ).agg(
            is_enemy.sum().alias("enemies_flashed"),
            is_team.sum().alias("team_flashed"),
            pl.col("blind_duration")
            .filter(is_enemy)
            .sum()
            .alias("blind_time"),
        )

    counts = ["flashes_thrown","enemies_flashed", "team_flashed", "flash_assists", "he_damage", "molotov_damage"]
    player_df = (
        players.join(flash_stats, on="steamid", how="left")
        .join(throws, on="steamid", how="left")
        .join(flash_assists, on="steamid", how="left")
        .join(he, on="steamid", how="left")
        .join(molotov, on="steamid", how="left")
        .with_columns(pl.col(counts).fill_null(0), pl.col("blind_time").fill_null(0.0))
        .select("steamid", "name", "team", *counts, "blind_time")
        .sort("enemies_flashed", descending=True)
    )
    return {"teams": build_teams(player_df, rounds)}