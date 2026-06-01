from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    SECRET_KEY: str
    ANTHROPIC_API_KEY: str = ""
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = ""
    MEILI_MASTER_KEY: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
