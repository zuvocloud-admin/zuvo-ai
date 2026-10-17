import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file into environment variables
load_dotenv()


class AppSettings(BaseSettings):
    name: str = "ZuvoCloud WhatsApp AI Operations Platform"
    version: str = "1.0.0"
    env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000


class DatabaseSettings(BaseSettings):
    url: str = "sqlite+aiosqlite:///./zuvo_local.db"
    echo_sql: bool = False
    pool_size: int = 20
    max_overflow: int = 10


class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"
    idempotency_ttl_seconds: int = 86400  # 24 hours


class WhatsAppSettings(BaseSettings):
    meta_api_version: str = "v20.0"
    base_url: str = "https://graph.facebook.com"
    verify_token: str = "zuvo_secret_verify_token_jaipur_2026"
    app_secret: str = "mock_meta_app_secret"
    system_user_token: str = "mock_system_user_token"
    phone_number_id: Optional[str] = None
    waba_id: Optional[str] = None
    request_timeout_seconds: int = 10


class SecuritySettings(BaseSettings):
    require_hmac_verification: bool = False
    allowed_origins: List[str] = ["*"]


class Settings(BaseSettings):
    """
    Centralized Configuration Model.
    Supports YAML base configuration with Environment Variable overrides.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    whatsapp: WhatsAppSettings = Field(default_factory=WhatsAppSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @classmethod
    def load_from_yaml_and_env(cls, yaml_path: Optional[str] = None) -> "Settings":
        """Loads configuration from YAML file and applies environment overrides."""
        config_data: Dict[str, Any] = {}
        
        # Default config path
        if not yaml_path:
            base_dir = Path(__file__).resolve().parent.parent.parent
            default_yaml = base_dir / "config" / "config.yaml"
            if default_yaml.exists():
                yaml_path = str(default_yaml)

        if yaml_path and os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}

        # Environment variable overrides
        db_url_env = os.getenv("DATABASE_URL")
        if db_url_env:
            config_data.setdefault("database", {})["url"] = db_url_env

        redis_url_env = os.getenv("REDIS_URL")
        if redis_url_env:
            config_data.setdefault("redis", {})["url"] = redis_url_env

        verify_token_env = os.getenv("META_VERIFY_TOKEN")
        if verify_token_env:
            config_data.setdefault("whatsapp", {})["verify_token"] = verify_token_env

        app_secret_env = os.getenv("META_APP_SECRET")
        if app_secret_env:
            config_data.setdefault("whatsapp", {})["app_secret"] = app_secret_env

        system_token_env = os.getenv("META_SYSTEM_USER_TOKEN")
        if system_token_env:
            config_data.setdefault("whatsapp", {})["system_user_token"] = system_token_env

        phone_num_id_env = os.getenv("META_PHONE_NUMBER_ID")
        if phone_num_id_env:
            config_data.setdefault("whatsapp", {})["phone_number_id"] = phone_num_id_env

        waba_id_env = os.getenv("META_WABA_ID")
        if waba_id_env:
            config_data.setdefault("whatsapp", {})["waba_id"] = waba_id_env

        api_version_env = os.getenv("META_API_VERSION")
        if api_version_env:
            config_data.setdefault("whatsapp", {})["meta_api_version"] = api_version_env

        hmac_env = os.getenv("REQUIRE_HMAC_VERIFICATION")
        if hmac_env is not None:
            config_data.setdefault("security", {})["require_hmac_verification"] = hmac_env.lower() in ("true", "1", "yes")

        return cls(**config_data)


# Global settings singleton
settings = Settings.load_from_yaml_and_env()
