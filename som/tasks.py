import math

from celery import Celery

from som.constants import BASE_HEIGHT, BASE_WIDTH
from som.domains.blueprint import SomBlueprintProcessor
from som.domains.models import SomArtBlueprint


app = Celery("tasks", broker="pyamqp://guest@localhost//")


def create_soms():
    w = math.ceil(BASE_WIDTH / 14)
    h = math.ceil(BASE_HEIGHT / 14)
    avg = (w + h) / 2
    bp = SomArtBlueprint(
        input_path="input-images/bee.jpg",
        width=w,
        height=h,
        epochs=4,
        learn_rates=[
            # 0.5,
            0.8,
            0.98,
        ],
        radius_sqs=[
            # round(avg_dim / 1),
            # round(avg / 2),
            # round(avg / 4),
            round(avg / 8),
            # round(math.pow(avg_dim / 7, 2)),
            # round(math.pow(avg_dim / 3, 2)),
        ],
        lr_decay=0.05,
        radius_decay=0.2,
        bucket="etsuko-io-som",
    )
    SomBlueprintProcessor(bp).run()


@app.task
def create_soms_task():
    create_soms()
