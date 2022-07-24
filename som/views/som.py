import kombu
from fastapi import HTTPException
from fastapi_utils.api_model import APIMessage
from loguru import logger

from som.domains.models import SomArtBlueprint
from som.tasks import create_soms_task


async def retrieve_som():
    return APIMessage(detail="Received item")


async def create_som(blueprint: SomArtBlueprint):
    try:
        create_soms_task.delay(blueprint.dict())
    except kombu.exceptions.OperationalError:
        logger.error("Can't connect to celery")
        raise HTTPException(status_code=500, detail="Failed to create task")

    return APIMessage(detail="Created item")
