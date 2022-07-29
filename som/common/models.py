from typing import List

from fastapi_utils.api_model import APIModel
from project_util.blueprint.blueprint import Blueprint


"""
The blueprint from the other art project u did was more extensive, it had actual
methods
"""


class ApiBlueprint(APIModel, Blueprint):
    pass


class SomArtBlueprint(ApiBlueprint):
    title: str
    width: int
    height: int
    bucket: str
    scale: float
    image: str
    # training params
    epochs: int
    learn_rates: List[float]
    sigmas: List[float]
    learning_rate_decay: float
    sigma_decay: float
