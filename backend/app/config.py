from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Réglages lus depuis l'environnement ou le fichier .env (racine du dépôt ou backend/)."""

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./declic.db"


settings = Settings()
