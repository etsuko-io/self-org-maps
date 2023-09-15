from pathlib import Path

import numpy as np
from loguru import logger
from src.project_util.artefact.artefact import Artefact
from src.project_util.blueprint.processor import BlueprintProcessor
from src.project_util.constants import S3, FILE_SYSTEM
from src.project_util.naming.naming import NamingUtil
from src.project_util.project.project import Project

from src.som.common.models import SomArtBlueprint
from src.som.worker.config.settings import WorkerSettings
from src.som.worker.domains.graphics import GraphicsDomain
from src.som.worker.domains.mail import Email
from src.som.worker.domains.som.som import SomDomain


class SomBlueprintProcessor:
    """
    Take a blueprint and process it.

    This class only calls other classes to the actual calculations.

    So the art class is separate; this is just converts the blueprint params
    to args for the art class.

    However, this class itself does save the art to the cloud/file system


    [ blueprint ]  >  [ processor ]   <->   [ art class ]
                            |                     |
                        [ saves artefacts ]    [ maths ]


    Alternative architecture:
    - processor provides save location to art class, and art class takes care
    itself of saving artefacts. is a good alternative, because maybe the art
    class saves arbitrary file formats that the processor class doesn't (need to)
    understand.

    Eventually this should be a very thin class

    You could make an auxilary class that translates "convenient" blueprint
    inputs to more granular params for the maths class.

    This is an "artistic" class, produces art output. Can you find something
    common with other of such classes, to unionize in a superclass/abc?

    - run() function
    - _log_plan()
    - _init_project(blueprint: Blueprint)

    - a main Project folder (Project class)
    - a parent directory
    - a project name
    - a Blueprint type
    - optional instance of NamingUtil
    """

    def __init__(self):
        logger.info("Processor instantiated")
        self.worker_settings: WorkerSettings = WorkerSettings()
        logger.info(f"Loaded worker settings: {self.worker_settings.dict()}")
        # super().__init__(
        #     name="hello"
        # )

    @staticmethod
    def _get_project_name(blueprint: SomArtBlueprint):
        return f"{NamingUtil.format_now()}-{blueprint.title}"

    def _init_project(self, blueprint: SomArtBlueprint) -> Project:
        # todo: Doesn't work / make sense for a Docker container to make local folders
        return Project(
            name=self._get_project_name(blueprint),
            parent_dir=Path(blueprint.path),
            blueprint=blueprint,
        )

    @staticmethod
    def _log_plan(blueprint: SomArtBlueprint):
        logger.info(
            f"{blueprint.epochs} epochs based on {blueprint.title}, "
            f"@{blueprint.width}x{blueprint.height}px"
        )
        logger.info(f"learn rate: {blueprint.learn_rate}")
        logger.info(f"radius sq: {blueprint.sigma}")
        logger.info(
            f"dim: {blueprint.width} x {blueprint.height} " f"@ scale {blueprint.scale}"
        )

    def _make_email(self, blueprint: SomArtBlueprint) -> Email:
        sender = "SOM Queue <rubencronie@gmail.com>"
        recipient = "rubencronie@gmail.com"
        subject = "Amazon SES Test (SDK for Python)"
        url = (
            f"https://s3.console.aws.amazon.com/s3/buckets/{blueprint.bucket}"
            f"?region=eu-west-1&tab=objects"
        )
        body_text = f"Your image '{blueprint.title}' is ready: {url}"

        # The HTML body of the email.
        body_html = f"""<html>
            <head></head>
            <body>
              <h1>Image is ready</h1>
              <p>Your image <b>{blueprint.title}</b> is ready.
                <a href='{url}'>Go to the bucket here</a>
                <p>Blueprint:</p>
                <p>{blueprint.json()}</p>
              </p>
            </body>
            </html>
        """
        return Email(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
        )

    def process(self, blueprint: SomArtBlueprint):
        logger.info("Processing started")
        proj = self._init_project(blueprint)
        self._log_plan(blueprint)
        som_single = SomDomain(
            height=blueprint.height,
            width=blueprint.width,
            scale=blueprint.scale,
            b64_image=blueprint.image,
            # same for multiple variations, so part of init
        )

        # todo: if you want to save individual epochs, you need to return
        # per epoch, or return a list of epochs
        logger.info(f"LR{blueprint.learn_rate} - R{blueprint.sigma}")
        result = som_single.train(
            step_divider=2,
            epochs=blueprint.epochs,
            learn_rate=blueprint.learn_rate,
            lr_decay=blueprint.learning_rate_decay,
            sigma=blueprint.sigma,
            radius_decay=blueprint.sigma_decay,
        )
        logger.info("Saving artefact...")
        artefact = Artefact(
            f"img_LR{blueprint.learn_rate}-R{blueprint.sigma}-{blueprint.title}.tiff",
            project=proj,
            data=np.uint8(result),
        )
        proj.save_image(
            artefact.data,
            file_name=Path(artefact.name),
            bucket=blueprint.bucket,
        )
        logger.info("Saving superres(x9)...")
        artefact_superres = artefact.get_superres(9)
        proj.save_image(
            artefact_superres.data,
            file_name=Path(artefact_superres.name),
            bucket=blueprint.bucket,
        )
        proj.save_file(
            content=blueprint.json(),
            file_name="blueprint.json",
            bucket=blueprint.bucket,
        )
        self._make_email(blueprint).send()
