import json
from pathlib import Path

from app.config import settings


def demos_dir() -> Path:
    path = settings.data_dir / "demos"
    path.mkdir(parents=True, exist_ok=True)
    return path


def match_dir(match_id: str) -> Path:
    return settings.data_dir / "matches" / match_id


def read_meta(match_id: str) -> dict | None:
    path = match_dir(match_id) / "meta.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_meta(match_id: str, meta: dict) -> None:
    path = match_dir(match_id) / "meta.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def create_meta(match_id: str, filename: str | None, owner: str) -> dict:
    meta = {
        "id": match_id,
        "owner": owner,
        "filename": filename,
        "status": "processing",
        "map_name": None,
        "tickrate": None,
        "rounds": None,
        "error": None,
    }
    write_meta(match_id, meta)
    return meta


def update_meta(match_id: str, **fields) -> dict:
    meta = read_meta(match_id) or {}
    meta.update(fields)
    write_meta(match_id, meta)
    return meta


def list_matches(owner: str) -> list[dict]:
    root = settings.data_dir / "matches"
    if not root.exists():
        return []
    metas = [read_meta(folder.name) for folder in sorted(root.iterdir()) if folder.is_dir()]
    return [meta for meta in metas if meta and meta.get("owner") == owner]