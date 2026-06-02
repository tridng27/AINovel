from minio import Minio

from app.core.config import settings

_client: Minio | None = None
COVER_BUCKET = "novel-covers"


def get_minio() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )
    return _client


def ensure_buckets() -> None:
    client = get_minio()
    if not client.bucket_exists(COVER_BUCKET):
        client.make_bucket(COVER_BUCKET)
