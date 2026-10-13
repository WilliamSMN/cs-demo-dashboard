import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import steam_auth


@pytest.fixture
def make_client(monkeypatch):
    """Fabrique des clients de test indépendants, avec ou sans session."""

    def factory(steamid: str | None = None) -> TestClient:
        client = TestClient(app)
        if steamid is not None:

            async def fake_verify(params, return_to, client=None):
                return steamid

            monkeypatch.setattr(steam_auth, "verify_steam_response", fake_verify)
            client.get("/auth/steam/callback?openid.mode=id_res", follow_redirects=False)
        return client

    return factory