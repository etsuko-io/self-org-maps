from typing import List

from pydantic import BaseModel


"""
The blueprint from the other art project u did was more extensive, it had actual
methods
"""


class SomArtBlueprint(BaseModel):
    input_path: str
    width: int
    height: int
    epochs: int
    learn_rates: List
    radius_sqs: List
    lr_decay: float
    radius_decay: float
