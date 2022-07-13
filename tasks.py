import math

from celery import Celery

from blueprint_domain import BlueprintProcessor
from constants import BASE_HEIGHT, BASE_WIDTH
from models import SomArtBlueprint


app = Celery("tasks", broker="pyamqp://guest@localhost//")


@app.task
def create_soms():
    w = math.ceil(BASE_WIDTH / 18)
    h = math.ceil(BASE_HEIGHT / 18)
    avg = (w + h) / 2
    bp = SomArtBlueprint(
        input_path="input-images/tokyo-station.jpeg",
        width=w,
        height=h,
        epochs=2,
        learn_rates=[
            # 0.5,
            0.75,
            0.99,
        ],
        radius_sqs=[
            # round(avg_dim / 1),
            round(avg / 2),
            round(avg / 4),
            # round(avg / 8),
            # round(math.pow(avg_dim / 7, 2)),
            # round(math.pow(avg_dim / 3, 2)),
        ],
        lr_decay=0.05,
        radius_decay=0.2,
    )
    BlueprintProcessor(bp).run()
