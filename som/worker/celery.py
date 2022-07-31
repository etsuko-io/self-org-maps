import os
from typing import Dict

from celery import Celery
from dotenv import load_dotenv
from loguru import logger

from som.common.models import SomArtBlueprint
from som.worker.domains.processor import SomBlueprintProcessor


def verify_env():
    failed = False
    if not os.environ.get("AWS_ACCESS_KEY_ID") or not os.environ.get(
        "AWS_SECRET_ACCESS_KEY"
    ):
        logger.error("$AWS_ACCESS_KEY_ID and $AWS_SECRET_ACCESS_KEY not found")
        logger.info(f"CWD: {os.getcwd()}")
        # failed = True > don't fail just yet,
        # on prod not required because EC2 instance profile
    if not os.environ.get("CELERY_BROKER"):
        logger.error("$CELERY_BROKER not found")
        failed = True
    if failed:
        raise RuntimeError("ENV vars are incomplete")


def create_celery():
    logger.info("Creating Celery")
    logger.info("Loading .env...")
    load_dotenv()
    verify_env()
    """
    URL format for SQS broker: sqs://aws_access_key_id:aws_secret_access_key@

    If you are using IAM roles on instances, you can set the BROKER_URL to:
    sqs://
    and kombu will attempt to retrieve access tokens from the instance metadata.
    """

    return Celery("tasks", broker=os.environ.get("CELERY_BROKER"))


celery = create_celery()


@celery.task
def create_soms_task(blueprint: Dict):
    blueprint_obj = SomArtBlueprint(**blueprint)
    SomBlueprintProcessor().process(blueprint_obj)
