from functools import lru_cache
import os


class Settings:
    app_name: str = "Digital Twin Prototype"
    api_prefix: str = "/api"

    def __init__(self) -> None:
        self.database_url = (
            os.getenv("SQLSERVER_CONNECTION_STRING")
            or os.getenv("DATABASE_URL")
            or ""
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
