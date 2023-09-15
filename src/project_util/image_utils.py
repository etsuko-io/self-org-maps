import os
from os.path import abspath, isdir, isfile, join
from pathlib import Path
from typing import List, Union

import cv2
from numpy import ndarray


def list_images(path: Union[str, Path], extensions=None) -> List[Path]:
    if not extensions:
        extensions = [".png", ".jpg", ".jpeg", ".tif", ".tiff"]
    if not isdir(path):
        raise ValueError(f"{path} is not a directory")
    paths = sorted(
        [
            abspath(join(path, f))
            for f in os.listdir(path)
            if not f.startswith(".")
            and isfile(join(path, f))
            and Path(f).suffix in extensions
        ],
        key=str.lower,
    )
    return [Path(p) for p in paths]


def load_images(paths: List[Union[str, Path]]) -> List[ndarray]:
    frames = []
    for p in paths:
        if isinstance(p, Path):
            frames.append(cv2.imread(p.as_posix()))
        else:
            frames.append(cv2.imread(p))

    return frames
