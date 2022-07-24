import os
from typing import Dict

from celery import Celery
from dotenv import load_dotenv
from loguru import logger

from som.domains.models import SomArtBlueprint
from som.domains.processor import SomBlueprintProcessor


def create_celery():
    logger.info("Loading .env...")
    load_dotenv()
    if not os.environ.get("AWS_ACCESS_KEY_ID") or not os.environ.get(
        "AWS_SECRET_ACCESS_KEY"
    ):
        logger.error("$AWS_ACCESS_KEY_ID and $AWS_SECRET_ACCESS_KEY not found")
        logger.info(f"CWD: {os.getcwd()}")
    if not os.environ.get("CELERY_BROKER"):
        logger.error("$CELERY_BROKER not found")
    return Celery("tasks", broker=os.environ.get("CELERY_BROKER"))


celery = create_celery()


@celery.task
def create_soms_task(blueprint: Dict):
    blueprint_obj = SomArtBlueprint(**blueprint)
    SomBlueprintProcessor().run(blueprint_obj)
