import json
from typing import Optional

from fastapi_utils.api_model import APIModel

from src.project_util.blueprint.blueprint import Blueprint


class ApiBlueprint(APIModel, Blueprint):
    def export(self) -> str:
        return json.dumps(self.dict(), indent=4)


class SomArtBlueprint(ApiBlueprint):
    title: str
    width: int
    height: int
    backend: str  # FILE_SYSTEM, S3
    bucket: Optional[str]
    path: str  # path within bucket
    scale: float  # applied to height and width
    image: str  # as base64
    # training params
    epochs: int
    learn_rate: float
    sigma: float
    learning_rate_decay: float
    sigma_decay: float
