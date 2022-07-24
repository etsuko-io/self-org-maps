from fastapi_utils.api_model import APIMessage

from som.domains.models import SomArtBlueprint
from som.tasks import create_soms


async def retrieve_som():
    return APIMessage(detail="Received item")


async def create_som(blueprint: SomArtBlueprint):
    await create_soms(blueprint)
    return APIMessage(detail="Created item")
