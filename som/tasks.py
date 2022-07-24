from celery import Celery

from som.domains.models import SomArtBlueprint
from som.domains.processor import SomBlueprintProcessor


app = Celery("tasks", broker="pyamqp://guest@localhost//")


async def create_soms(blueprint: SomArtBlueprint):
    await SomBlueprintProcessor().run(blueprint)


@app.task
def create_soms_task():
    create_soms()
