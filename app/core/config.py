from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "5500 Backend"
    app_env: str = "dev"
    port: int = 8000

    # Database
    database_url: str = (
        "postgresql+psycopg://qr_survey_user:qr_survey_password@localhost:5432/qr_survey_db"
    )

    # JWT
    jwt_secret: str = "change_me_in_production"
    jwt_expire_hours: int = 24

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Public app URL for QR codes
    public_app_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
