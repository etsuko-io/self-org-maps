import math
import os.path
from abc import ABC
from os.path import join
from pathlib import Path

import numpy as np
from loguru import logger
from PIL import Image
from project_util.artefact.artefact import Artefact
from project_util.naming.naming import NamingUtil
from project_util.project.project import Project

from som.domains.graphics import GraphicsDomain
from som.domains.models import Blueprint, SomArtBlueprint
from som.domains.som.som import SomDomain


class BlueprintProcessor(ABC):
    def __init__(self, *args, **kwargs):
        pass

    def process(self, blueprint: Blueprint):
        raise NotImplementedError


class SomBlueprintProcessor(BlueprintProcessor):
    """
    Take a blueprint and process it.
    Todo: make generic ABC, add to ProjectUtil
    """

    def process(self, blueprint: SomArtBlueprint):
        # todo: use this instead of requiring __init__
        pass

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
        self.input_file_name = os.path.splitext(Path(self.input_path).name)[0]
        self.img_width = blueprint.width
        self.img_height = blueprint.height
        self.epochs = blueprint.epochs
        self.avg_dim = (self.img_width + self.img_height) / 2
        self.learn_rates = blueprint.learn_rates
        self.radius_sqs = blueprint.radius_sqs
        self.lr_decay = blueprint.lr_decay
        self.radius_decay = blueprint.radius_decay
        self.proj = self._init_project()
        self.train_data = self._load_train_data()
        self.bucket = blueprint.bucket
        super().__init__()

    def _get_project_name(self):
        return f"{NamingUtil.format_now()}-{self.input_file_name}"

    def _init_project(self) -> Project:
        parent_dir = Path(join(Path(__file__).parent.parent.parent.resolve(), "results"))
        return Project(name=self._get_project_name(), parent_dir=parent_dir)

    def _load_train_data(self):
        with Image.open(self.input_path) as im:
            im = im.convert("RGB")
            return np.array(im).reshape((-1, 3))

    def _log_plan(self):
        logger.info(
            f"{self.epochs} epochs based on {self.input_path}, "
            f"@{self.img_width}x{self.img_height}px"
        )
        logger.info(f"learn rates: {self.learn_rates}")
        logger.info(f"radius sqs: {self.radius_sqs}")
        logger.info(f"dim: {self.img_width} x {self.img_height}")

    def run(self):
        self._log_plan()
        som_single = SomDomain(
            height=self.img_height,
            width=self.img_width,
            train_data=self.train_data,
            # same for multiple variations, so part of init
        )

        # todo: if you want to save individual epochs, you need to return per epoch,
        #  or return a list of epochs
        for lr in self.learn_rates:
            for sigma in self.radius_sqs:
                logger.info(f"LR{lr} - R{sigma}")
                result = som_single.train(
                    step=math.ceil(self.avg_dim / 2),
                    epochs=self.epochs,
                    learn_rate=lr,
                    lr_decay=self.lr_decay,
                    radius_sq=sigma,
                    radius_decay=self.radius_decay,
                )
                artefact = Artefact(
                    f"img_LR{lr}-R{sigma}-{self.input_file_name}.tiff",
                    project=self.proj,
                    data=np.uint8(result),
                )
                artefact.save()
                artefact.save_to_s3(bucket=self.bucket)
                artefact_superres = artefact.get_superres(
                    9, new_project=self.proj.add_folder("x9")
                )
                artefact_superres.save()
                artefact_superres.save_to_s3(bucket=self.bucket)
        GraphicsDomain.create_blend_animation(
            input_proj=self.proj.folders["x9"],
            output_proj=self.proj.folders["x9"].add_folder("animation"),
            name="animation",
            frames_per_blend=96,
        )
