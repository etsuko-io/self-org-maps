import os.path
from functools import lru_cache
from typing import Optional, Tuple, TypeVar

import cv2
import numpy as np
from cv2 import dnn_superres
from PIL import Image

from src.project_util.naming.naming import NamingUtil
from src.project_util.project.project import Project


TArtefact = TypeVar("TArtefact", bound="Artefact")


class Artefact:
    # Class is candidate to move to image-specific lib
    def __init__(
        self,
        name: str,
        project: Optional[Project] = None,
        size: Optional[Tuple[int, int]] = None,
        data: Optional[np.ndarray] = None,
    ):
        if data is None and size is None:
            raise ValueError("Data or size should be defined")
        self.name = name
        self.project = project
        self.data = data  # when in color, should always be RGB(A)
        self.size = size
        if data is not None:
            self._update_size()
        else:
            self.fill((0, 0, 0))

    def _update_size(self):
        self.size = self.data.shape[0], self.data.shape[1]

    @property
    def width(self):
        return self.size[0] if self.size else None

    @property
    def height(self):
        return self.size[1] if self.size else None

    def update(self, data: np.ndarray):
        self.data = data
        self._update_size()

    def get_superres(
        self,
        upscale: int = 4,
        new_name: Optional[str] = None,
        new_project: Optional[Project] = None,
    ) -> TArtefact:
        """
        Return a version of the current artefact in an AI-upsampled resolution
        :param project:
        :param new_name:
        :param upscale: 2, 3, 4, 6, 8, 9, 12, or 16
        :return:
        """
        upscales = (2, 3, 4, 6, 8, 9, 12, 16)
        if upscale not in upscales:
            raise ValueError(f"Upscale should be one of {upscales}")
        upscaled_img = None
        if upscale < 5:
            superres = self.get_superres_ml_model(upscale)
            upscaled_img = superres.upsample(self.data)
        elif upscale == 6:
            superres2 = self.get_superres_ml_model(2)
            superres3 = self.get_superres_ml_model(3)
            upscaled_img = superres2.upsample(superres3.upsample(self.data))
        elif upscale == 8:
            superres2 = self.get_superres_ml_model(2)
            superres4 = self.get_superres_ml_model(4)
            upscaled_img = superres2.upsample(superres4.upsample(self.data))
        elif upscale == 9:
            superres3 = self.get_superres_ml_model(3)
            upscaled_img = superres3.upsample(superres3.upsample(self.data))
        elif upscale == 12:
            superres3 = self.get_superres_ml_model(3)
            superres4 = self.get_superres_ml_model(4)
            upscaled_img = superres3.upsample(superres4.upsample(self.data))
        elif upscale == 16:
            superres4 = self.get_superres_ml_model(4)
            upscaled_img = superres4.upsample(superres4.upsample(self.data))
        return Artefact(
            name=new_name or NamingUtil.insert_suffix(self.name, suffix=f"@x{upscale}"),
            data=upscaled_img,
            project=new_project or self.project,
        )

    @staticmethod
    @lru_cache
    def get_superres_ml_model(upscale):
        superres = dnn_superres.DnnSuperResImpl_create()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # todo: download this.
        model_path = os.path.join(current_dir, f"ml-models/EDSR_x{upscale}.pb")
        superres.readModel(model_path)
        # Set the desired model and scale to get correct
        # pre- and post-processing
        superres.setModel("edsr", upscale)
        return superres

    @staticmethod
    def cv2_to_pil(data: np.ndarray) -> Image:
        return Image.fromarray(cv2.cvtColor(data, cv2.COLOR_BGR2RGB))

    @staticmethod
    def pil_to_cv2(img: Image) -> np.ndarray:
        pil_as_arr = np.array(img)
        return cv2.cvtColor(pil_as_arr, cv2.COLOR_RGB2BGR)

    def fill(self, rgb: Tuple) -> None:
        image: Image = Image.new("RGB", self.size)
        image.paste(rgb, [0, 0, self.width, self.height])
        self.data = np.array(image)
