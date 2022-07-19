from fastapi_utils.api_model import APIMessage

from som.tasks import create_soms


async def retrieve_som():
    return APIMessage(detail="Received item")


async def create_som():
    create_soms()
    return APIMessage(detail="Created item")
