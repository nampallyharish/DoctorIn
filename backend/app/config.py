"""Configuration settings management via Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "DoctorIn"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000

    # Database
    POSTGRES_USER: str = "doctorin"
    POSTGRES_PASSWORD: str = "doctorin_dev_password"
    POSTGRES_DB: str = "doctorin"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = (
        "postgresql+asyncpg://doctorin:doctorin_dev_password@localhost:5432/doctorin"
    )
    DATABASE_URL_SYNC: str = (
        "postgresql://doctorin:doctorin_dev_password@localhost:5432/doctorin"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "insecure-dev-secret-change-in-production-min-32-chars-now"
    JWT_REFRESH_SECRET: str = "insecure-dev-refresh-secret-change-in-production-min-32"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # OTP & Email Settings
    OTP_PROVIDER: str = "development"  # 'development', 'resend', 'sms', 'email'
    OTP_PROVIDER_API_KEY: str = ""
    OTP_PROVIDER_SECRET: str = ""
    OTP_EXPIRY_MINUTES: int = 5
    OTP_EXPIRY_SECONDS: int = 300  # 5 minutes
    OTP_MAX_ATTEMPTS: int = 5
    OTP_MAX_REQUESTS_PER_HOUR: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60

    # Email Delivery
    # EMAIL_PROVIDER options:
    #   'smtp'        → send via Gmail or any SMTP server (recommended for personal use)
    #   'resend'      → send via Resend API (requires RESEND_API_KEY)
    #   'development' → print OTP to terminal only, no real email
    EMAIL_PROVIDER: str = "development"
    EMAIL_FROM: str = "DoctorIn <your@gmail.com>"

    # SMTP (Gmail / Outlook / any SMTP server)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""   # your full Gmail address
    SMTP_PASSWORD: str = ""   # Gmail App Password (NOT your login password)
    SMTP_USE_TLS: bool = True  # True for Gmail port 587

    # Resend API (alternative to SMTP)
    RESEND_API_KEY: str = ""

    # S3 Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "doctorin"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,"
        "http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002"
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def clean_smtp_password(self) -> str:
        """Strip spaces and whitespace from Google App Password."""
        return (self.SMTP_PASSWORD or "").replace(" ", "").strip()

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
