from typing import List

from fastapi_utils.api_model import APIModel


"""
The blueprint from the other art project u did was more extensive, it had actual
methods
"""


class Blueprint(APIModel):
    pass


class SomArtBlueprint(Blueprint):
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
