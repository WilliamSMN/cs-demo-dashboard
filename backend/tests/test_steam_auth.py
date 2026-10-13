import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import steam_auth
from app.services.steam_auth import verify_steam_response

RETURN_TO = "http://localhost:8000/auth/steam/callback"
STEAMID = "76561198996627086"


def valid_params(**overrides):
    params = {
        "openid.mode": "id_res",
        "openid.return_to": RETURN_TO,
        "openid.claimed_id": f"https://steamcommunity.com/openid/id/{STEAMID}",
    }
    return {**params, **overrides}


async def run(handler, params):
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        return await verify_steam_response(params, RETURN_TO, client=client)


def test_valid_response_returns_steamid():
    def handler(request: httpx.Request) -> httpx.Response:
        assert b"check_authentication" in request.content
        return httpx.Response(200, text="ns:http://specs.openid.net/auth/2.0\nis_valid:true\n")

    assert asyncio.run(run(handler, valid_params())) == STEAMID


def test_steam_rejecting_the_response_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="is_valid:false\n")

    assert asyncio.run(run(handler, valid_params())) is None


def test_claimed_id_from_another_site_is_rejected_without_calling_steam():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("Steam ne doit pas être appelé")

    params = valid_params(**{"openid.claimed_id": f"https://evil.example/openid/id/{STEAMID}"})
    assert asyncio.run(run(handler, params)) is None


def test_return_to_mismatch_is_rejected():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("Steam ne doit pas être appelé")

    params = valid_params(**{"openid.return_to": "http://evil.example/callback"})
    assert asyncio.run(run(handler, params)) is None


@pytest.fixture
def client():
    return TestClient(app)


def test_me_without_session_is_401(client):
    assert client.get("/auth/me").status_code == 401


def test_login_redirects_to_steam(client):
    response = client.get("/auth/steam/login", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"].startswith("https://steamcommunity.com/openid/login")


def test_callback_opens_a_session_then_logout_closes_it(client, monkeypatch):
    async def fake_verify(params, return_to, client=None):
        return STEAMID

    monkeypatch.setattr(steam_auth, "verify_steam_response", fake_verify)

    response = client.get("/auth/steam/callback?openid.mode=id_res", follow_redirects=False)
    assert response.status_code == 302
    assert client.get("/auth/me").json() == {"steamid": STEAMID}

    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/me").status_code == 401


def test_failed_verification_redirects_to_login_error(client, monkeypatch):
    async def fake_verify(params, return_to, client=None):
        return None

    monkeypatch.setattr(steam_auth, "verify_steam_response", fake_verify)

    response = client.get("/auth/steam/callback?openid.mode=id_res", follow_redirects=False)
    assert response.headers["location"].endswith("/login?error=steam")
    assert client.get("/auth/me").status_code == 401