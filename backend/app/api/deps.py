from fastapi import HTTPException, Request


def current_steamid(request: Request) -> str:
    steamid = request.session.get("steamid")
    if not steamid:
        raise HTTPException(status_code=401, detail="Not signed in")
    return steamid