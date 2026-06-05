import json

from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    SECRET_KEY: str

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("SECRET_KEY must not be empty")
        try:
            parsed = json.loads(v)
        except json.JSONDecodeError:
            return v  # chuỗi thường (vd hex) → hợp lệ
        if not isinstance(parsed, str):
            raise ValueError(
                "SECRET_KEY là giá trị JSON ('null'/'true'/số) — python-jose sẽ "
                "parse thành None và làm hỏng JWT. Hãy dùng chuỗi hex ngẫu nhiên."
            )
        return v
    ANTHROPIC_API_KEY: str = ""
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = ""
    MEILI_MASTER_KEY: str = ""

    # Email / SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@ainovel.app"
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
