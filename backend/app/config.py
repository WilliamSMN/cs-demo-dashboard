from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"

    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:4200"

    session_secret: str = "dev-only-change-me"
    cookie_secure: bool = False 
    
    steam_api_key: str = ""


settings = Settings()