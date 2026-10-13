import re
from urllib.parse import urlencode

import httpx

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
OPENID_NS = "http://specs.openid.net/auth/2.0"
IDENTIFIER_SELECT = "http://specs.openid.net/auth/2.0/identifier_select"
CLAIMED_ID_RE = re.compile(r"^https://steamcommunity\.com/openid/id/(\d{17})$")


def build_login_url(return_to: str, realm: str) -> str:
    params = {
        "openid.ns": OPENID_NS,
        "openid.mode": "checkid_setup",
        "openid.return_to": return_to,
        "openid.realm": realm,
        "openid.identity": IDENTIFIER_SELECT,
        "openid.claimed_id": IDENTIFIER_SELECT,
    }
    return f"{STEAM_OPENID_URL}?{urlencode(params)}"


async def verify_steam_response(
    params: dict[str, str],
    expected_return_to: str,
    client: httpx.AsyncClient | None = None,
) -> str | None:
    """Renvoie le SteamID64 si la réponse est authentique, sinon None."""
    if params.get("openid.mode") != "id_res":
        return None
    if params.get("openid.return_to") != expected_return_to:
        return None
    claimed = CLAIMED_ID_RE.match(params.get("openid.claimed_id", ""))
    if claimed is None:
        return None

    check = {**params, "openid.mode": "check_authentication"}
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=10)
    try:
        response = await client.post(STEAM_OPENID_URL, data=check)
    except httpx.HTTPError:
        return None
    finally:
        if owns_client:
            await client.aclose()

    if response.status_code != 200 or "is_valid:true" not in response.text:
        return None
    return claimed.group(1)