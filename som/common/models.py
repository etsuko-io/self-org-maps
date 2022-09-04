import json

from fastapi_utils.api_model import APIModel
from project_util.blueprint.blueprint import Blueprint


class ApiBlueprint(APIModel, Blueprint):
    def export(self) -> str:
        return json.dumps(self.dict(), indent=4)


class SomArtBlueprint(ApiBlueprint):
    title: str
    width: int
    height: int
    bucket: str
    path: str  # path within bucket
    scale: float
    image: str
    # training params
    epochs: int
    learn_rate: float
    sigma: float
    learning_rate_decay: float
    sigma_decay: float
