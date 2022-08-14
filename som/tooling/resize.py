import argparse
import base64
import io
import os
from math import ceil, sqrt
from os.path import isfile, join
from pathlib import Path

from loguru import logger
from PIL import Image
from project_util.project.project import Project

from som.common.models import SomArtBlueprint


parser = argparse.ArgumentParser(description="Resize images for training.")

parser.add_argument("path", type=str, help="file/folder to resize")


def downsize_image(img: Image, training_length: int):
    scale = sqrt(current_length / training_length)
    return img.resize(size=(ceil(img.width / scale), ceil(img.height / scale)))


def img_to_b64(img: Image) -> str:
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")


def make_request_body(name, b64_img):
    bp = SomArtBlueprint(
        **{
            "width": 1920,
            "height": 1080,
            "scale": 0.3,
            "epochs": 4,
            "learnRate": 0.8,
            "sigma": 0.1,
            "learningRateDecay": 0.05,
            "sigmaDecay": 0.2,
            "bucket": "etsuko-io-som",
            "path": "/results",
            "title": name,
            "image": b64_img,
        }
    )
    return bp.json(indent=4)


if __name__ == "__main__":
    args = parser.parse_args()
    training_length = 5000
    path = Path(args.path).absolute()
    project_location = path.parent
    files = [path]

    if path.is_dir():
        files = [
            join(path, f)
            for f in os.listdir(path)
            if isfile(join(path, f)) and not f.startswith(".")
        ]

    project = Project(name="blueprints", parent_dir=path)
    print(f"project location: {project.path}")

    for f in files:
        with Image.open(f) as img:
            current_length = img.width * img.height
            if current_length <= training_length:
                logger.info("Image already at correct size")
            else:
                img = downsize_image(img, training_length=5000)

            img_b64 = img_to_b64(img)
            """
            TL = training_length
            w/x * h/x = TL
            (w*h)/x^2 = TL
            w*h       = TL * x^2
            w*h / TL  = x^2
            x         = sqrt(w*h/TL)

            below, x = scale
            """

        file_name = os.path.splitext(Path(f).name)[0]
        # project.save_file(content=img_b64, file_name=f"{file_name}.txt")
        project.save_file(
            content=make_request_body(name=file_name, b64_img=img_b64),
            file_name=f"{file_name}.txt",
        )
