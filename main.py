import math
from os.path import join
from pathlib import Path

import numpy as np
from PIL import Image
from project_util.artefact.artefact import Artefact
from project_util.naming.naming import NamingUtil
from project_util.project.project import Project

from constants import BASE_WIDTH, BASE_HEIGHT
from graphics import Graphics
from models import SomArtBlueprint
from som import SingleSom

"""
todos for structure: 
[x] A single instance should actually just be a single map
[ ] The provided input should be in-memory, not a path
[ ] What the SOM class returns, should be in-memory, not written anywhere yet
[ ] Displaying with matplotlib should be optional and separated
[ ] get_complexity() should be an external method, from an analyzer 
[ ] make somap.train() return a Somap model that includes metadata 
"""


class Main:
    # This is an "artistic" class, produces art output. Can you find something
    # common with other of such classes, to unionize in a superclass/abc?
    # - a run() function
    # - a main Project folder (Project class)
    # - a parent directory
    # - a project name
    # - a Blueprint type
    # - optional instance of NamingUtil

    def __init__(self, blueprint: SomArtBlueprint):
        self.blueprint = blueprint
        self.input_path = blueprint.input_path
        self.img_width = blueprint.width
        self.img_height = blueprint.height
        self.epochs = 2
        self.avg_dim = (self.img_width + self.img_height) / 2
        self.learn_rates = blueprint.learn_rates
        self.radius_sqs = blueprint.radius_sqs
        self.lr_decay = blueprint.lr_decay
        self.radius_decay = blueprint.radius_decay
        self.proj = self._init_project()
        self.train_data = self._load_train_data()

    @staticmethod
    def _get_project_name():
        return f"{NamingUtil.format_now()}-{NamingUtil.random_name()}"

    def _init_project(self) -> Project:
        parent_dir = Path(join(Path(__file__).parent.resolve(), "results"))
        return Project(name=self._get_project_name(), parent_dir=parent_dir)

    def _load_train_data(self):
        with Image.open(self.input_path) as im:
            im = im.convert("RGB")
            return np.array(im).reshape((-1, 3))

    def _log_plan(self):
        print(
            f"{self.epochs} epochs based on {self.input_path}, "
            f"@{self.img_width}x{self.img_height}px"
        )
        print(f"learn rates: {self.learn_rates}")
        print(f"radius sqs: {self.radius_sqs}")

    def run(self):
        self._log_plan()
        som_single = SingleSom(
            height=self.img_height,
            width=self.img_width,
            train_data=self.train_data,
            # same for multiple variations, so part of init
        )
        # todo: if you want to save individual epochs, you need to return per epoch,
        #  or return a list of epochs
        for lr in self.learn_rates:
            for sigma in self.radius_sqs:
                print(f"LR{lr} - R{sigma}")
                result = som_single.train(
                    step=math.ceil(self.avg_dim / 2),
                    epochs=self.epochs,
                    learn_rate=lr,
                    lr_decay=self.lr_decay,
                    radius_sq=sigma,
                    radius_decay=self.radius_decay,
                )
                artefact = Artefact(
                    f"img_LR{lr}-R{sigma}.tiff",
                    project=self.proj,
                    data=np.uint8(result),
                )
                artefact.save()
                artefact.get_superres(
                    9, new_project=self.proj.add_folder("x9")
                ).save()
        Graphics.create_blend_animation(
            input_proj=self.proj.folders["x9"],
            output_proj=self.proj.folders["x9"].add_folder("animation"),
            name="animation",
            frames_per_blend=96,
        )


if __name__ == "__main__":
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
    Main(bp).run()
