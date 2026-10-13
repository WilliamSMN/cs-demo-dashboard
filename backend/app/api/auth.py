from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.services import steam_auth
from app.api.deps import current_steamid

router = APIRouter(prefix="/auth", tags=["auth"])


def callback_url() -> str:
    return f"{settings.backend_url}/auth/steam/callback"


@router.get("/steam/login")
def steam_login():
    url = steam_auth.build_login_url(return_to=callback_url(), realm=settings.backend_url)
    return RedirectResponse(url, status_code=302)


@router.get("/steam/callback")
async def steam_callback(request: Request):
    params = {k: v for k, v in request.query_params.items() if k.startswith("openid.")}
    steamid = await steam_auth.verify_steam_response(params, callback_url())
    if steamid is None:
        return RedirectResponse(f"{settings.frontend_url}/login?error=steam", status_code=302)

    request.session.clear()  # évite de réutiliser une ancienne session
    request.session["steamid"] = steamid
    return RedirectResponse(settings.frontend_url, status_code=302)


@router.get("/me")
def me(steamid: Annotated[str, Depends(current_steamid)]):
    return {"steamid": steamid}


@router.post("/logout", status_code=204)
def logout(request: Request):
    request.session.clear()