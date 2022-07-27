import base64
import io
import math
from abc import ABC
from os.path import join
from pathlib import Path

import numpy as np
from fastapi import HTTPException, UploadFile
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

    def __init__(self):
        super().__init__()

    @staticmethod
    def _get_project_name(blueprint):
        return f"{NamingUtil.format_now()}-{blueprint.title}"

    def _init_project(self, blueprint: SomArtBlueprint) -> Project:
        parent_dir = Path(
            join(Path(__file__).parent.parent.parent.resolve(), "results")
        )
        return Project(
            name=self._get_project_name(blueprint), parent_dir=parent_dir
        )

    @staticmethod
    def _load_train_data(input_path):
        with Image.open(input_path) as im:
            im = im.convert("RGB")
            # reshape so it's a 1-dimensional array of color values
            return np.array(im).reshape((-1, 3))

    @staticmethod
    async def _load_train_data_from_bytes(file: UploadFile):
        contents = await file.read()
        im = Image.open(io.BytesIO(contents))
        # reshape so it's a 1-dimensional array of color values
        return np.array(im).reshape((-1, 3))

    @staticmethod
    def _load_train_data_from_base64(base64_str: str):
        try:
            im = Image.open(
                io.BytesIO(base64.decodebytes(bytes(base64_str, "utf-8")))
            )
            im.show()
        except Exception as e:
            logger.error(f"Error loading image base64: {e}")
            raise HTTPException(
                status_code=400, detail="Error loading base64 image"
            )

        return np.array(im).reshape((-1, 3))

    def _log_plan(self, blueprint: SomArtBlueprint):
        logger.info(
            f"{blueprint.epochs} epochs based on {blueprint.title}, "
            f"@{blueprint.width}x{blueprint.height}px"
        )
        logger.info(f"learn rates: {blueprint.learn_rates}")
        logger.info(f"radius sqs: {blueprint.sigmas}")
        logger.info(
            f"dim: {blueprint.width} x {blueprint.height} "
            f"@ scale {blueprint.scale}"
        )

    def run(self, blueprint: SomArtBlueprint):
        width = math.ceil(blueprint.width * blueprint.scale)
        height = math.ceil(blueprint.height * blueprint.scale)
        avg_dim = (width + height) / 2

        # train_data = self._load_train_data(blueprint.input_path)
        train_data = self._load_train_data_from_base64(
            blueprint.image,
        )

        proj = self._init_project(blueprint)
        self._log_plan(blueprint)
        som_single = SomDomain(
            height=height,
            width=width,
            train_data=train_data,
            # same for multiple variations, so part of init
        )

        # todo: if you want to save individual epochs, you need to return
        # per epoch, or return a list of epochs
        for lr in blueprint.learn_rates:
            for sigma in blueprint.sigmas:
                logger.info(f"LR{lr} - R{sigma}")
                result = som_single.train(
                    step=math.ceil(avg_dim / 2),
                    epochs=blueprint.epochs,
                    learn_rate=lr,
                    lr_decay=blueprint.learning_rate_decay,
                    radius_sq=round(sigma * avg_dim),
                    radius_decay=blueprint.sigma_decay,
                )
                artefact = Artefact(
                    f"img_LR{lr}-R{sigma}-{blueprint.title}.tiff",
                    project=proj,
                    data=np.uint8(result),
                )
                artefact.save()
                artefact.save_to_s3(bucket=blueprint.bucket)
                artefact_superres = artefact.get_superres(
                    9, new_project=proj.add_folder("x9")
                )
                artefact_superres.save()
                artefact_superres.save_to_s3(bucket=blueprint.bucket)
        GraphicsDomain.create_blend_animation(
            input_proj=proj.folders["x9"],
            output_proj=proj.folders["x9"].add_folder("animation"),
            name="animation",
            frames_per_blend=24,
        )