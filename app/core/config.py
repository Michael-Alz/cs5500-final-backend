# app/core/config.py
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------------------- #
    #  App Configuration     #
    # ---------------------- #
    app_name: str = Field("5500 Backend", validation_alias="APP_NAME")
    app_env: str = Field("dev", validation_alias="APP_ENV")
    port: int = Field(8000, validation_alias="PORT")

    # ---------------------- #
    #  Database Configuration
    # ---------------------- #
    # Use the Docker service name "database" for internal connections
    database_url: str = Field(
        "postgresql+psycopg://class_connect_user:class_connect_password@database:5432/class_connect_db",
        validation_alias="DATABASE_URL",
    )

    # ---------------------- #
    #  JWT Configuration     #
    # ---------------------- #
    jwt_secret: str = Field("change_me_in_production", validation_alias="JWT_SECRET")
    jwt_expire_hours: int = Field(24, validation_alias="JWT_EXPIRE_HOURS")

    # ---------------------- #
    #  CORS Configuration    #
    # ---------------------- #
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        validation_alias="CORS_ORIGINS",
    )
    admin_emails: List[str] = Field(default=[], validation_alias="ADMIN_EMAILS")

    # Support both JSON arrays and comma-separated strings
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            v = v.strip()
            # If JSON array: starts with "["
            if v.startswith("["):
                import json

                return json.loads(v)
            # Otherwise treat as comma-separated list
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("admin_emails", mode="before")
    @classmethod
    def parse_admin_emails(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                import json

                return json.loads(v)
            return [email.strip() for email in v.split(",") if email.strip()]
        return v

    # ---------------------- #
    #  Public App URL        #
    # ---------------------- #
    public_app_url: str = Field("http://localhost:5173", validation_alias="PUBLIC_APP_URL")

    # ---------------------- #
    #  Pydantic Config       #
    # ---------------------- #
    model_config = SettingsConfigDict(
        # Load local .env file (for standalone dev runs)
        env_file=".env",
        env_file_encoding="utf-8",
        # Do not require prefixes like APP_ or BACKEND_
        env_prefix="",
        # Case-insensitive keys (APP_NAME == app_name)
        case_sensitive=False,
        # Ignore any extra environment variables
        extra="ignore",
    )


# Instantiate settings once for global use
settings = Settings()
