import hashlib
from typing import Annotated
from uuid import uuid4

import polars as pl
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, UploadFile

from app.analysis.stats import compute_player_stats, compute_trade_stats, compute_utility_stats, compute_clutch_stats
from app.analysis.report import build_player_summary, build_round_impact, build_kill_timing, build_opening_duels, build_extras
from app.api.deps import current_steamid
from app.schemas import MatchMeta, StatsResponse, TradesResponse, UtilityResponse, ClutchResponse, PlayerReportSummary, RoundImpactResponse, KillTimingResponse, OpeningDuelsResponse, ExtrasResponse
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

def get_ready_meta(match_id: str, owner: str) -> dict:
    meta = get_own_meta_or_404(match_id, owner)
    if meta["status"] != "ready":
        raise HTTPException(status_code=409, detail=f"Match non prêt (statut : {meta['status']})")
    return meta


def load_tables(match_id: str, *tables: str) -> dict[str, pl.DataFrame]:
    folder = store.match_dir(match_id)
    return {t: pl.read_parquet(folder / f"{t}.parquet") for t in tables}


def load_match(match_id: str, owner: str, *tables: str) -> dict[str, pl.DataFrame]:
    get_ready_meta(match_id, owner)
    return load_tables(match_id, *tables)


def tickrate_of(meta: dict) -> float:
    return meta.get("tickrate") or 64


def or_404(result, detail: str = "Joueur absent de ce match"):
    if result is None:
        raise HTTPException(status_code=404, detail=detail)
    return result


# Les noms des tables correspondent aux noms des paramètres des fonctions d'analyse,
# ce qui permet de les passer avec **t.

@router.get("/{match_id}/stats", response_model=StatsResponse)
def get_stats(match_id: MatchId, owner: Owner):
    t = load_match(match_id, owner, "kills", "damages", "rounds", "players")
    return compute_player_stats(**t)


@router.get("/{match_id}/trades", response_model=TradesResponse)
def get_trades(match_id: MatchId, owner: Owner):
    meta = get_ready_meta(match_id, owner)
    t = load_tables(match_id, "kills", "rounds", "players")
    return compute_trade_stats(**t, tickrate=tickrate_of(meta))


@router.get("/{match_id}/utility", response_model=UtilityResponse)
def get_utility(match_id: MatchId, owner: Owner):
    t = load_match(
        match_id, owner, "kills", "damages", "flashes", "flash_throws", "players", "rounds"
    )
    return compute_utility_stats(**t)


@router.get("/{match_id}/clutch", response_model=ClutchResponse)
def get_clutch(match_id: MatchId, owner: Owner):
    t = load_match(match_id, owner, "kills", "players", "rounds")
    return compute_clutch_stats(**t)


@router.get("/{match_id}/report/summary", response_model=PlayerReportSummary)
def get_report_summary(match_id: MatchId, owner: Owner):
    t = load_match(match_id, owner, "kills", "damages", "rounds", "players")
    return or_404(build_player_summary(**t, steamid=owner))


@router.get("/{match_id}/report/rounds", response_model=RoundImpactResponse)
def get_report_rounds(match_id: MatchId, owner: Owner):
    t = load_match(match_id, owner, "kills", "damages", "rounds", "players")
    return or_404(build_round_impact(**t, steamid=owner))


@router.get("/{match_id}/report/timing", response_model=KillTimingResponse)
def get_report_timing(match_id: MatchId, owner: Owner):
    meta = get_ready_meta(match_id, owner)
    t = load_tables(match_id, "kills", "rounds", "players")
    return or_404(build_kill_timing(**t, steamid=owner, tickrate=tickrate_of(meta)))


@router.get("/{match_id}/report/opening", response_model=OpeningDuelsResponse)
def get_report_opening(match_id: MatchId, owner: Owner):
    t = load_match(match_id, owner, "kills", "players")
    return or_404(build_opening_duels(**t, steamid=owner))


@router.get("/{match_id}/report/extras", response_model=ExtrasResponse)
def get_report_extras(match_id: MatchId, owner: Owner):
    meta = get_ready_meta(match_id, owner)
    t = load_tables(
        match_id, "kills", "damages", "flashes", "flash_throws", "players", "rounds"
    )
    return or_404(build_extras(**t, steamid=owner, tickrate=tickrate_of(meta)))