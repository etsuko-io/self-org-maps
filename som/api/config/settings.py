from pydantic import BaseSettings


class ApiSettings(BaseSettings):
    celery_broker: str
