import hashlib
from typing import Annotated
from uuid import uuid4

import polars as pl
from fastapi import APIRouter, BackgroundTasks, HTTPException, Path, UploadFile

from app.analysis.stats import compute_player_stats
from app.schemas import MatchMeta, StatsResponse
from app.services import store
from app.services.ingest import ingest_demo

router = APIRouter(prefix="/matches", tags=["matches"])

# L'identifiant est un hash hexadécimal : on refuse tout autre format dans l'URL
MatchId = Annotated[str, Path(pattern=r"^[0-9a-f]{12}$")]


def get_meta_or_404(match_id: str) -> dict:
    meta = store.read_meta(match_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="Match introuvable")
    return meta


@router.post("", status_code=202, response_model=MatchMeta)
async def upload_match(file: UploadFile, background_tasks: BackgroundTasks):
    if not (file.filename or "").lower().endswith(".dem"):
        raise HTTPException(status_code=400, detail="Un fichier .dem est attendu")

    # Ecriture par blocs (les démos pèsent plusieurs centaines de Mo) + hash du contenu
    tmp = store.demos_dir() / f"upload-{uuid4().hex}.tmp"
    digest = hashlib.sha256()
    with tmp.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            digest.update(chunk)
            out.write(chunk)

    match_id = digest.hexdigest()[:12]
    existing = store.read_meta(match_id)
    if existing and existing["status"] != "failed":
        tmp.unlink()  # même démo déjà envoyée : on ne la retraite pas
        return existing

    final = store.demos_dir() / f"{match_id}.dem"
    tmp.replace(final)
    meta = store.create_meta(match_id, filename=file.filename)
    background_tasks.add_task(ingest_demo, match_id, final)
    return meta


@router.get("", response_model=list[MatchMeta])
def list_matches():
    return store.list_matches()


@router.get("/{match_id}", response_model=MatchMeta)
def get_match(match_id: MatchId):
    return get_meta_or_404(match_id)


@router.get("/{match_id}/stats", response_model=StatsResponse)
def get_stats(match_id: MatchId):
    meta = get_meta_or_404(match_id)
    if meta["status"] != "ready":
        raise HTTPException(status_code=409, detail=f"Match non prêt (statut : {meta['status']})")

    folder = store.match_dir(match_id)
    kills = pl.read_parquet(folder / "kills.parquet")
    damages = pl.read_parquet(folder / "damages.parquet")
    rounds = pl.read_parquet(folder / "rounds.parquet")
    players = pl.read_parquet(folder / "players.parquet")

    stats = compute_player_stats(kills, damages, rounds, players).with_columns(
        pl.col("steamid").cast(pl.String)
    )
    return StatsResponse(
        players=stats.to_dicts(),
        unattributed_deaths=kills["victim_steamid"].null_count(),
    )