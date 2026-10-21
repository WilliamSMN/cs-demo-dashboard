from app.analysis.report import build_extras, build_opening_duels, build_player_summary

# (plancher, moyenne, plafond) : valeurs estimées, à calibrer avec de vraies parties
SCALES = {
    "hs_pct": (0.25, 0.45, 0.65),
    "impact": (0.3, 1.0, 1.7),
    "utility_damage_pr": (0.0, 5.0, 15.0),
    "enemies_flashed_pr": (0.0, 0.3, 0.9),
    "clutch_win_rate": (0.0, 0.25, 0.6),
    "opening_win_rate": (0.2, 0.5, 0.75),
    "trade_kills_pr": (0.0, 0.12, 0.3),
}


def _score(name: str, value: float | None) -> float | None:
    """0 au plancher, 50 à la moyenne, 100 au plafond (borné)."""
    if value is None:
        return None
    floor, avg, ceiling = SCALES[name]
    if value <= avg:
        s = 50 * (value - floor) / (avg - floor)
    else:
        s = 50 + 50 * (value - avg) / (ceiling - avg)
    return round(max(0.0, min(100.0, s)), 1)


def _rate(flags: list[bool]) -> float | None:
    return sum(flags) / len(flags) if flags else None


def _r(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(value, digits)


def build_profile(
    kills, damages, flashes, flash_throws, rounds, players, steamid: str, tickrate: float
) -> dict | None:
    summary = build_player_summary(kills, damages, rounds, players, steamid, tickrate)
    extras = build_extras(
        kills, damages, flashes, flash_throws, rounds, players, steamid, tickrate
    )
    opening = build_opening_duels(kills, players, steamid)
    if summary is None or extras is None or opening is None or not summary["rounds"]:
        return None

    n = summary["rounds"]
    impact = 2.13 * summary["kills"] / n + 0.42 * summary["assists"] / n - 0.41
    util = extras["utility"]
    util_damage = (util["he_damage"] + util["molotov_damage"]) / n
    flashed = util["enemies_flashed"] / n
    trade_kills = extras["trades"]["trade_kills"] / n

    clutches = extras["clutches"]
    clutch_rate = _rate([c["won"] for c in clutches])
    duels = opening["duels"]
    opening_rate = _rate([d["won"] for d in duels])

    util_scores = [_score("utility_damage_pr", util_damage), _score("enemies_flashed_pr", flashed)]

    axes = [
        {"key": "aim", "score": _score("hs_pct", summary["hs_pct"]),
         "values": {"hs_pct": _r(summary["hs_pct"])}},
        {"key": "impact", "score": _score("impact", impact),
         "values": {"impact": _r(impact, 2)}},
        {"key": "utility", "score": round(sum(util_scores) / len(util_scores), 1),
         "values": {"damage_per_round": _r(util_damage, 2), "enemies_flashed_per_round": _r(flashed, 2)}},
        {"key": "clutch", "score": _score("clutch_win_rate", clutch_rate),
         "values": {"win_rate": _r(clutch_rate), "attempts": len(clutches)}},
        {"key": "opening", "score": _score("opening_win_rate", opening_rate),
         "values": {"win_rate": _r(opening_rate), "attempts": len(duels)}},
        {"key": "trade", "score": _score("trade_kills_pr", trade_kills),
         "values": {"trade_kills_per_round": _r(trade_kills, 2)}},
    ]
    return {"axes": axes}