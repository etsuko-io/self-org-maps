import json
from abc import ABC

from fastapi_utils.api_model import APIModel


class Blueprint(ABC):
    def export(self) -> str:
        """
        This should return a string representing the blueprint in a way that could be
        neatly printed to the command line or saved as a (text) file.
        :return: human-readable JSON/YAML/Dict/.. of the blueprint
        """
        raise NotImplementedError


class ApiBlueprint(APIModel, Blueprint):
    """
    Blueprint base class tailored for use with Pydantic and FastAPI.
    Can be used for (de)serializig API requests and responses, as it will convert
    between snake_case and camelCase appropriately.
    """

    def export(self) -> str:
        return json.dumps(self.dict(), indent=4)
