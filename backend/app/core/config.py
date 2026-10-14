import os
from dataclasses import dataclass
from urllib.parse import urlparse

from arq.connections import RedisSettings
from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://sales_app:change-me@localhost:5432/sales_analyzer",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    api_key: str | None = os.getenv("APP_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    
    openai_base_url: str = os.getenv(
        "OPENAI_BASE_URL", 
        "https://api.metisai.ir/api/v1/wrapper/openai" 
    )
    
    openai_model: str = os.getenv(
        "OPENAI_MODEL", 
        "gpt-4o-mini" 
    )
    farsava_api_key: str | None = os.getenv("FARSAVA_API_KEY")
    farsava_url: str = os.getenv(
        "FARSAVA_URL",
        "https://api.amerandish.com/v1/speech2text",
    )
    dynamics_tenant_id: str | None = os.getenv("DYNAMICS_TENANT_ID")
    dynamics_client_id: str | None = os.getenv("DYNAMICS_CLIENT_ID")
    dynamics_client_secret: str | None = os.getenv("DYNAMICS_CLIENT_SECRET")
    dynamics_env_url: str | None = os.getenv("DYNAMICS_ENV_URL")
    audio_directory: str = os.getenv("AUDIO_DIRECTORY", "/shared_audio")
    audio_url_allowed_hosts: tuple[str, ...] = _split_csv(
        os.getenv("AUDIO_URL_ALLOWED_HOSTS", "")
    )
    cors_origins: tuple[str, ...] = _split_csv(
        os.getenv("CORS_ORIGINS", "http://localhost:3000")
    )

    def redis_settings(self) -> RedisSettings:
        parsed = urlparse(self.redis_url)
        return RedisSettings(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            database=int((parsed.path or "/0").lstrip("/") or 0),
            password=parsed.password,
        )

    def require_dynamics(self) -> None:
        missing = [
            name
            for name, value in (
                ("DYNAMICS_TENANT_ID", self.dynamics_tenant_id),
                ("DYNAMICS_CLIENT_ID", self.dynamics_client_id),
                ("DYNAMICS_CLIENT_SECRET", self.dynamics_client_secret),
                ("DYNAMICS_ENV_URL", self.dynamics_env_url),
            )
            if not value or value.startswith("your_")
        ]
        if missing:
            raise RuntimeError(f"Missing Dynamics configuration: {', '.join(missing)}")


settings = Settings()
