from typing import Optional

from pydantic import BaseSettings


class WorkerSettings(BaseSettings):
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    celery_broker: str
    enable_animation: bool
    save_local: bool
    has_gui: bool
