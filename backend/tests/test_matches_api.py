import polars as pl
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import store

client = TestClient(app)

# Plus grand que 2**53 : serait arrondi si envoyé comme nombre JSON à du JavaScript
BIG_STEAMID = 76561198996627086


@pytest.fixture(autouse=True)
def tmp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)


def test_upload_rejects_non_dem_file():
    response = client.post("/matches", files={"file": ("notes.txt", b"hello")})
    assert response.status_code == 400


def test_unknown_match_returns_404():
    assert client.get("/matches/abcdef123456").status_code == 404


def test_stats_refused_while_processing():
    store.create_meta("abcdef123456", filename="demo.dem")
    assert client.get("/matches/abcdef123456/stats").status_code == 409


def test_stats_serializes_steamid_as_string_and_reports_unattributed_deaths():
    match_id = "abcdef123456"
    store.create_meta(match_id, filename="demo.dem")
    store.update_meta(match_id, status="ready")
    folder = store.match_dir(match_id)

    pl.DataFrame(
        [(1, 100, BIG_STEAMID, "t", None, None, None, None, None, True)],
        schema={
            "round_num": pl.UInt32, "tick": pl.Int64,
            "attacker_steamid": pl.UInt64, "attacker_side": pl.String,
            "victim_steamid": pl.UInt64, "victim_name": pl.String, "victim_side": pl.String,
            "assister_steamid": pl.UInt64, "assister_side": pl.String,
            "headshot": pl.Boolean,
        },
        orient="row",
    ).write_parquet(folder / "kills.parquet")
    pl.DataFrame(
        [],
        schema={
            "round_num": pl.UInt32, "attacker_steamid": pl.UInt64,
            "attacker_side": pl.String, "victim_side": pl.String,
            "dmg_health_real": pl.Int64,
        },
    ).write_parquet(folder / "damages.parquet")
    pl.DataFrame({"round_num": [1]}, schema={"round_num": pl.UInt32}).write_parquet(
        folder / "rounds.parquet"
    )
    pl.DataFrame(
        {"steamid": [BIG_STEAMID], "name": ["WilloKage"]},
        schema={"steamid": pl.UInt64, "name": pl.String},
    ).write_parquet(folder / "players.parquet")

    response = client.get(f"/matches/{match_id}/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["players"][0]["steamid"] == str(BIG_STEAMID)
    assert body["players"][0]["kills"] == 1
    assert body["unattributed_deaths"] == 1