from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import matches

app = FastAPI(title="CS Demo Dashboard")

# Autorise le serveur de dev Angular à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router)

@app.get("/health")
def health():
    return {"status": "ok"}