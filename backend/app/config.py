from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Réglages lus depuis l'environnement ou le fichier .env (racine du dépôt ou backend/)."""

    # Chemins absolus : le .env est trouvé quel que soit le dossier d'où on lance l'API.
    model_config = SettingsConfigDict(env_file=(BACKEND_DIR.parent / ".env", BACKEND_DIR / ".env"), extra="ignore")

    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./declic.db"

    jwt_secret: str = Field(min_length=32)  # obligatoire : pas de valeur par défaut devinable
    jwt_expire_days: int = 30

    # Pseudos autorisés sur /admin/stats, séparés par des virgules (ex. « teddy,lea »)
    admin_pseudos: str = ""

    def is_admin(self, pseudo: str) -> bool:
        return pseudo.lower() in {p.strip().lower() for p in self.admin_pseudos.split(",") if p.strip()}

    openai_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    llm_vision_model: str = "gpt-4.1-mini"


settings = Settings()  # type: ignore[call-arg]  # jwt_secret vient de l'environnement
