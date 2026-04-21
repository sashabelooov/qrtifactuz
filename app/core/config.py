from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    SECRET_KEY: str
    DEBUG: bool = False
    SHOW_DOCS: bool = True

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "qrtifact"
    AWS_S3_REGION: str = "us-east-1"

    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # Admin panel
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_SECRET_KEY: str
    ADMIN_CREDENTIALS: str = ""  # "user1:pass1,user2:pass2" for multiple admins

    def get_admin_credentials(self) -> dict[str, str]:
        """Returns {username: password} for all admins."""
        creds = {self.ADMIN_USERNAME: self.ADMIN_PASSWORD}
        if self.ADMIN_CREDENTIALS:
            for pair in self.ADMIN_CREDENTIALS.split(","):
                if ":" in pair:
                    u, p = pair.strip().split(":", 1)
                    creds[u] = p
        return creds


settings = Settings()
