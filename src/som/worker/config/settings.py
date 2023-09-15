from typing import Optional

from pydantic import BaseSettings


class WorkerSettings(BaseSettings):
    # automatically loads from .env file
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    celery_broker: str
    enable_animation: bool
    storage_backend: str
    has_gui: bool

    class Config:
        env_file = ".env"
