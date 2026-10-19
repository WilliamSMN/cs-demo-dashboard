from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import current_steamid
from app.services.steam_profile import get_steam_profile

router = APIRouter(prefix="/users", tags=["users"])


class SteamProfile(BaseModel):
    steamid: str
    name: str | None
    avatar: str | None
    is_public: bool


@router.get("/me/steam-profile", response_model=SteamProfile)
async def my_steam_profile(steamid: Annotated[str, Depends(current_steamid)]):
    try:
        profile = await get_steam_profile(steamid)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Steam is unavailable")
    if profile is None:
        raise HTTPException(status_code=404, detail="Steam profile not found")
    return SteamProfile(**profile)