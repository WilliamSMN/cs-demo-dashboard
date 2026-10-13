from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import auth, matches
from app.config import settings

app = FastAPI(title="CS Demo Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=settings.cookie_secure,
    max_age=14 * 24 * 3600,
)

app.include_router(auth.router)
app.include_router(matches.router)


@app.get("/health")
def health():
    return {"status": "ok"}