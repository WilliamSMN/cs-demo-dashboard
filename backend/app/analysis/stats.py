import polars as pl


def compute_player_stats(
    kills: pl.DataFrame,
    damages: pl.DataFrame,
    rounds: pl.DataFrame,
    players: pl.DataFrame,
) -> dict:
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

    # Récupération des scores finaux depuis le dernier round
    if "winner" in rounds.columns and rounds.height > 0:
        # On compte les rounds gagnés par CT et par T
        ct_wins = rounds.filter(pl.col("winner").str.to_uppercase() == "CT").height
        t_wins = rounds.filter(pl.col("winner").str.to_uppercase() == "T").height
    else:
        ct_wins, t_wins = 0, 0

    team_0_score = ct_wins
    team_1_score = t_wins

    # Transformation en dictionnaires pour le groupement par équipe
    all_players = player_df.with_columns(pl.col("steamid").cast(pl.String)).to_dicts()

    team_0_players = [p for p in all_players if p.get("team") == 0]
    team_1_players = [p for p in all_players if p.get("team") == 1]
    other_players = [p for p in all_players if p.get("team") not in (0, 1)]

    teams = [
        {
            "name": "Team 1",  # Ou "Equipe 0" / nom personnalisé
            "score": team_0_score,
            "players": team_0_players,
        },
        {
            "name": "Team 2",  # Ou "Equipe 1"
            "score": team_1_score,
            "players": team_1_players,
        }
    ]

    if other_players:
        teams.append({
            "name": "Spectateurs / Indéfinis",
            "score": 0,
            "players": other_players,
        })

    return {
        "teams": teams,
        "unattributed_deaths": kills["victim_steamid"].null_count(),
    }