import polars as pl
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import store

ALICE = "76561198000000001"
BOB = "76561198000000002"
BIG_STEAMID = 76561198996627086  # plus grand que 2**53 : serait arrondi en JavaScript
DEMO_BYTES = b"PBDEMS2\x00" + b"x" * 1024


@pytest.fixture(autouse=True)
def tmp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)


@pytest.fixture
def no_parsing(monkeypatch):
    """Evite de lancer le vrai parsing pendant les tests d'envoi."""
    monkeypatch.setattr("app.api.matches.ingest_demo", lambda match_id, path: None)


def upload(client, name="match.dem", content=DEMO_BYTES):
    return client.post("/matches", files={"file": (name, content)})


def test_anonymous_requests_are_rejected(make_client):
    anonymous = make_client()
    assert anonymous.get("/matches").status_code == 401
    assert upload(anonymous).status_code == 401
    assert anonymous.get("/matches/abcdef123456").status_code == 401


def test_upload_rejects_non_dem_file(make_client):
    alice = make_client(ALICE)
    assert upload(alice, name="notes.txt").status_code == 400


def test_unknown_match_returns_404(make_client):
    alice = make_client(ALICE)
    assert alice.get("/matches/abcdef123456").status_code == 404


def test_upload_creates_an_owned_match_without_leaking_the_owner(make_client, no_parsing):
    alice = make_client(ALICE)
    response = upload(alice)
    assert response.status_code == 202
    assert response.json()["status"] == "processing"
    assert "owner" not in response.json()
    assert len(alice.get("/matches").json()) == 1


def test_same_file_uploaded_twice_by_the_same_user_is_deduplicated(make_client, no_parsing):
    alice = make_client(ALICE)
    first = upload(alice).json()["id"]
    second = upload(alice).json()["id"]
    assert first == second
    assert len(alice.get("/matches").json()) == 1


def test_same_file_uploaded_by_two_users_gives_independent_matches(make_client, no_parsing):
    alice, bob = make_client(ALICE), make_client(BOB)
    alice_id = upload(alice).json()["id"]
    bob_id = upload(bob).json()["id"]
    assert alice_id != bob_id
    assert [m["id"] for m in alice.get("/matches").json()] == [alice_id]
    assert [m["id"] for m in bob.get("/matches").json()] == [bob_id]


def test_another_users_match_is_a_404(make_client, no_parsing):
    alice, bob = make_client(ALICE), make_client(BOB)
    alice_id = upload(alice).json()["id"]
    assert bob.get(f"/matches/{alice_id}").status_code == 404
    assert bob.get(f"/matches/{alice_id}/stats").status_code == 404


def test_stats_refused_while_processing(make_client):
    alice = make_client(ALICE)
    store.create_meta("abcdef123456", filename="demo.dem", owner=ALICE)
    assert alice.get("/matches/abcdef123456/stats").status_code == 409


def test_stats_serializes_steamid_as_string_and_reports_unattributed_deaths(make_client):
    alice = make_client(ALICE)
    match_id = "abcdef123456"
    store.create_meta(match_id, filename="demo.dem", owner=ALICE)
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
    
    # Ajout des scores pour que le dernier round ne plante pas
    pl.DataFrame(
        {"round_num": [1], "ct_score": [10], "t_score": [5]},
        schema={"round_num": pl.UInt32, "ct_score": pl.Int64, "t_score": pl.Int64}
    ).write_parquet(folder / "rounds.parquet")

    pl.DataFrame(
        {"steamid": [BIG_STEAMID], "name": ["WilloKage"], "team": [1]},
        schema={"steamid": pl.UInt64, "name": pl.String, "team": pl.Int64},
    ).write_parquet(folder / "players.parquet")

    response = alice.get(f"/matches/{match_id}/stats")
    
    assert response.status_code == 200
    body = response.json()
    
    # Récupération du joueur à travers le tableau des équipes (Team 2 correspond à team=1)
    team_1 = next(t for t in body["teams"] if t["name"] == "Team 2")
    player = team_1["players"][0]

    assert player["steamid"] == str(BIG_STEAMID)
    assert player["kills"] == 1
    assert player["team"] == 1
    assert body["unattributed_deaths"] == 1
    assert team_1["score"] == 5