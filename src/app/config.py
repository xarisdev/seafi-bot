from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

CURRENT_FILE_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_FILE_DIR.parent.parent

ENV_PATH = ROOT_DIR / ".env"

class Application(BaseSettings):
    ADMIN_ID: int
    TELEGRAM_BOT_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class APIClient(BaseSettings):
    X_API_KEY: str

    BASE_SERVER_URL: str
    WSS_CONNECT_SERVER_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class Settings(
    Application,
    APIClient
):
    pass

settings = Settings()