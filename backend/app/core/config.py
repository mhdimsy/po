from functools import lru_cache
import os
from pathlib import Path


def load_dotenv_if_present() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Settings:
    app_name: str = "Digital Twin Prototype"
    api_prefix: str = "/api"

    def __init__(self) -> None:
        load_dotenv_if_present()
        self.database_url = (
            os.getenv("SQLSERVER_CONNECTION_STRING")
            or os.getenv("DATABASE_URL")
            or ""
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
