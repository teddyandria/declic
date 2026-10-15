from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Réglages lus depuis l'environnement ou le fichier .env (racine du dépôt ou backend/)."""

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./declic.db"

    jwt_secret: str = Field(min_length=32)  # obligatoire : pas de valeur par défaut devinable
    jwt_expire_days: int = 30

    openai_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    llm_vision_model: str = "gpt-4.1-mini"


settings = Settings()  # type: ignore[call-arg]  # jwt_secret vient de l'environnement
