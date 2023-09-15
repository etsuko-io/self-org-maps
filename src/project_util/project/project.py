import io
import os
from os import listdir, makedirs
from os.path import isfile, join
from pathlib import Path
from typing import Dict, List, Optional, TypeVar, Union

import numpy as np
from loguru import logger
from PIL import Image

from src.project_util.constants import FILE_SYSTEM, S3
from src.project_util.image_utils import list_images, load_images
from src.project_util.services.s3 import S3Client
from src.som.common.models import SomArtBlueprint

TProject = TypeVar("TProject", bound="Project")


class Project:
    def __init__(
        self,
        name: str,
        parent_dir: Path,
        blueprint: SomArtBlueprint,
    ):
        self._parent_dir = parent_dir
        self._name = name
        # self._project_dir: Path = self._get_project_dir()
        self.folders: Dict[str, Project] = {}
        self._s3_client = None
        self.blueprint = blueprint

    @property
    def s3_client(self):
        if not self._s3_client:
            self._s3_client = S3Client()
        return self._s3_client

    def dir_of_file(self, file, parents: int):
        """Return the abs path of a __file__ variable"""
        # todo: implement

    def _get_project_dir(self):
        if self.blueprint.backend == FILE_SYSTEM:
            return Path(join(self._parent_dir, self._name)).absolute()
        elif self.blueprint.backend == S3:
            return Path(join(self._parent_dir, self._name))

    def _make_project_dir(self):
        if self.blueprint.backend == FILE_SYSTEM:
            makedirs(self.path, exist_ok=True)
        else:
            raise ValueError(f"Unsupported backend: {self.blueprint.backend}")

    def create_file_name(self, name: str) -> str:
        """
        Create a filename relative to the current project directory.
        Just an implementation of os.path.join() for the current project dir.
        :param name:
        :return:
        """
        return os.path.join(self._project_dir, name)

    def get_file_names(self):
        """
        Get all filenames in current project directory
        :return:
        """
        return [
            join(self.path, f) for f in listdir(self.path) if isfile(join(self.path, f))
        ]

    def load_images(self) -> List[np.ndarray]:
        # Candidate for moving to an image-specific project lib
        paths = list_images(self.path)
        logger.debug(f"Project path: {self.path}")
        logger.debug(f"Loading image paths: {paths}")
        return load_images(paths)

    def _require_backend(self, backend):
        if self.blueprint.backend != backend:
            raise RuntimeError(f"operation is only supported on backend {backend}")

    def save_file(
        self, content: str, file_name: str, bucket: Optional[str] = None
    ) -> str:
        path = join(self.blueprint.path, file_name)
        if self.blueprint.backend == FILE_SYSTEM:
            with open(path, "w") as file:
                file.write(content)
            return path
        elif self.blueprint.backend == S3:
            if not bucket:
                raise ValueError("bucket and path are required for saving to S3")
            return self._save_file_to_s3(content=content, bucket=bucket, path=path)

    def save_image(
        self,
        data: Union[np.ndarray, Image.Image],
        file_name: Union[str, Path],
        bucket: Optional[str] = None,
        img_format: str = "PNG",
    ) -> Union[Path, str]:
        # Candidate for moving to an image-specific project lib
        if isinstance(file_name, Path):
            file_name = file_name.as_posix()
        if self.blueprint.backend == S3:
            if not bucket:
                raise ValueError("bucket and path are required for saving to S3")
            return self._save_image_to_s3(
                data=data,
                bucket=bucket,
                path=os.path.join(self.path, file_name),
                img_format=img_format,
            )
        elif self.blueprint.backend == FILE_SYSTEM:
            return self._save_image_to_file_system(
                data, file_name, img_format=img_format
            )
        else:
            raise ValueError(f"{self.blueprint.backend} not supported")

    @classmethod
    def to_pillow(cls, data: Union[np.ndarray, Image.Image]):
        if isinstance(data, Image.Image):
            return data
        elif isinstance(data, np.ndarray):
            return Image.fromarray(np.uint8(data))
        raise ValueError(f"Unsupported data format: {type(data)}")

    def _save_image_to_file_system(
        self,
        data: Union[np.ndarray, Image.Image],
        file_name: Union[str, Path],
        img_format: str,
    ) -> str:
        # Candidate for moving to an image-specific project lib
        path = os.path.join(self.blueprint.path, file_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im = self.to_pillow(data)
        im.save(path, format=img_format)
        return os.path.abspath(path)

    def _save_image_to_s3(
        self,
        data: Union[np.ndarray, Image.Image],
        bucket: str,
        path: str,
        img_format: str,
    ) -> str:
        # Candidate for moving to an image-specific project lib
        im = self.to_pillow(data)
        im_bytes = io.BytesIO()
        im.save(im_bytes, format=img_format)

        result = self.s3_client.save(
            data=im_bytes.getvalue(),
            bucket=bucket,
            path=path,
        )
        return result.get("ETag")

    def _save_file_to_s3(self, content: str, bucket: str, path: str):
        result = self.s3_client.save(
            data=content.encode("utf-8"),
            bucket=bucket,
            path=path,
        )
        return result.get("ETag")

    def save_blueprint(self, file_name: Union[str, Path], bucket: Optional[str] = None):
        if not self.blueprint:
            raise ValueError("Blueprint not set")

        if self.blueprint.backend == S3:
            self._save_blueprint_to_s3(
                bucket=bucket, path=os.path.join(self.path, file_name)
            )

        else:
            raise NotImplementedError(f"Backend {self.blueprint.backend} not supported yet")

    def _save_blueprint_to_s3(self, bucket, path):
        data = self.blueprint.export()
        self.s3_client.save(
            data=data.encode("utf-8"),
            bucket=bucket,
            path=path,
        )

    def remove_folder(self, name: str) -> None:
        # todo: use abspath
        if self.blueprint.backend == FILE_SYSTEM:
            os.removedirs(self.path.joinpath(name))
        del self.folders[name]
