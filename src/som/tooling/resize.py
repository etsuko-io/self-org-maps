import argparse
import base64
import io
import os
from math import ceil, sqrt
from os.path import isfile, join
from pathlib import Path

from loguru import logger
from PIL import Image

from src.som.common.models import SomArtBlueprint


parser = argparse.ArgumentParser(description="Resize images for training.")

parser.add_argument("path", type=str, help="file/folder to resize")
parser.add_argument("pixels", type=int, help="number of pixels in result")

"""
Todo: if you really want a project tool, it should be a super bare bones file manager.
However, it should support 2 backends (S3 and File system).
"""


def downsize_image(img: Image, training_length: int):
    """
    Downsize an image so that its number of pixels (w*h) matches the desired training
    length.

    Formula (x = downsize factor = unknown)
    TL = training_length
    w/x * h/x = TL
    (w*h)/x^2 = TL
    w*h       = TL * x^2
    w*h / TL  = x^2
    x         = sqrt(w*h/TL)

    below, x = scale
    """
    scale = sqrt(img.width * img.height / training_length)
    return img.resize(size=(ceil(img.width / scale), ceil(img.height / scale)))


def img_to_b64(img: Image) -> str:
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")


def make_request_body(name, b64_img):
    bp = SomArtBlueprint(
        width=1920,
        height=1080,
        scale=0.15,
        epochs=3,
        learnRate=0.8,
        backend="FILE_SYSTEM",
        learningRateDecay=0.05,
        sigma=0.3,
        sigmaDecay=0.2,
        bucket="etsuko-io-som",
        path="results",
        title=name,
        image=b64_img,
    )
    return bp.json(indent=4)


def save_file(
    self,
    content: str,
    file_name: str,
    path: str,
) -> str:
    path = join(path, file_name)
    with open(path, "w") as file:
        file.write(content)
    return path


if __name__ == "__main__":
    args = parser.parse_args()
    training_length = args.pixels
    path = Path(args.path).absolute()
    project_location = path.parent
    files = [path]

    if path.is_dir():
        files = [
            join(path, f)
            for f in os.listdir(path)
            if isfile(join(path, f)) and not f.startswith(".")
        ]

    for f in files:
        with Image.open(f) as img:
            img = img.convert("RGB")
            current_length = img.width * img.height
            if current_length <= training_length:
                logger.info("Image already at correct size")
            else:
                img = downsize_image(img, training_length=5000)

            img_b64 = img_to_b64(img)

        file_name = os.path.splitext(Path(f).name)[0]
        output_path = project_location.joinpath(file_name + ".txt")
        with open(output_path, "w") as file:
            file.write(img_b64)
        logger.info(
            f"Resized image saved as base64 in folder: file://{project_location}"
        )
        logger.info(f"File: file://{output_path.absolute()}")
