import hashlib
from typing import Annotated
from uuid import uuid4

import polars as pl
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, UploadFile

from app.analysis.stats import compute_player_stats
from app.api.deps import current_steamid
from app.schemas import MatchMeta, StatsResponse
from app.services import store
from app.services.ingest import ingest_demo

router = APIRouter(prefix="/matches", tags=["matches"])

# L'identifiant est un hash hexadécimal : on refuse tout autre format dans l'URL
MatchId = Annotated[str, Path(pattern=r"^[0-9a-f]{12}$")]
Owner = Annotated[str, Depends(current_steamid)]


def get_own_meta_or_404(match_id: str, owner: str) -> dict:
    meta = store.read_meta(match_id)
    # 404 aussi pour le match d'un autre : on ne révèle pas son existence
    if meta is None or meta.get("owner") != owner:
        raise HTTPException(status_code=404, detail="Match introuvable")
    return meta


@router.post("", status_code=202, response_model=MatchMeta)
async def upload_match(file: UploadFile, background_tasks: BackgroundTasks, owner: Owner):
    if not (file.filename or "").lower().endswith(".dem"):
        raise HTTPException(status_code=400, detail="Un fichier .dem est attendu")

    # Ecriture par blocs (les démos pèsent plusieurs centaines de Mo).
    # L'identifiant dépend du propriétaire ET du contenu : deux utilisateurs qui
    # envoient le même fichier obtiennent deux matchs indépendants.
    tmp = store.demos_dir() / f"upload-{uuid4().hex}.tmp"
    digest = hashlib.sha256(owner.encode() + b"\0")
    with tmp.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            digest.update(chunk)
            out.write(chunk)

    match_id = digest.hexdigest()[:12]
    existing = store.read_meta(match_id)
    if existing and existing["status"] != "failed":
        tmp.unlink()  # même démo déjà envoyée par ce même utilisateur
        return existing

    final = store.demos_dir() / f"{match_id}.dem"
    tmp.replace(final)
    meta = store.create_meta(match_id, filename=file.filename, owner=owner)
    background_tasks.add_task(ingest_demo, match_id, final)
    return meta


@router.get("", response_model=list[MatchMeta])
def list_matches(owner: Owner):
    return store.list_matches(owner)


@router.get("/{match_id}", response_model=MatchMeta)
def get_match(match_id: MatchId, owner: Owner):
    return get_own_meta_or_404(match_id, owner)


@router.get("/{match_id}/stats", response_model=StatsResponse)
def get_stats(match_id: MatchId, owner: Owner):
    meta = get_own_meta_or_404(match_id, owner)
    if meta["status"] != "ready":
        raise HTTPException(status_code=409, detail=f"Match non prêt (statut : {meta['status']})")

    folder = store.match_dir(match_id)
    kills = pl.read_parquet(folder / "kills.parquet")
    damages = pl.read_parquet(folder / "damages.parquet")
    rounds = pl.read_parquet(folder / "rounds.parquet")
    players = pl.read_parquet(folder / "players.parquet")

    result = compute_player_stats(kills, damages, rounds, players)
    return StatsResponse(**result)