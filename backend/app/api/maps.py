from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse

from app.analysis.radar import radar_path

router = APIRouter(prefix="/maps", tags=["maps"])

MapName = Annotated[str, Path(pattern=r"^[a-z0-9_]{3,40}$")]


@router.get("/{map_name}/radar")
def get_radar(map_name: MapName):
    path = radar_path(map_name)
    if path is None:
        raise HTTPException(status_code=404, detail="Radar introuvable")
    return FileResponse(
        path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"}
    )