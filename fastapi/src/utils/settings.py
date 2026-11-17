
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get project root directory
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    # Database connection from .env
    DB_CONNECTION: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )


# Initialize settings
settings = Settings()
