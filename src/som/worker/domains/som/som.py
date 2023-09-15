import base64
import io
import math

import numpy as np
from loguru import logger
from numpy import ndarray
from PIL import Image

from src.som.tooling.entropy import grayscale_4bit
from src.som.worker.domains.som import som_math


class SomDomain:
    def __init__(
        self,
        width: int,
        height: int,
        scale: float,
        b64_image: str,
    ):
        self.width = math.ceil(width * scale)
        self.height = math.ceil(height * scale)
        self.train_data = self._load_train_data_from_base64(b64_image)

    @property
    def avg_dim(self):
        return (self.width + self.height) / 2

    @staticmethod
    def _load_train_data_from_base64(base64_str: str):
        try:
            im = Image.open(io.BytesIO(base64.decodebytes(bytes(base64_str, "utf-8"))))
        except Exception as e:
            logger.error(f"Error loading image base64: {e}")
            raise ValueError("Error loading base64 image")

        return np.array(im).reshape((-1, 3))

    def get_random_grid(self):
        rand = np.random.RandomState(0)
        somap = rand.randint(0, 256, (self.height, self.width, 3)).astype(float)
        return somap

    def train(
        self,
        step_divider: int,
        epochs: int,
        learn_rate: float,
        lr_decay: float,
        sigma: float,
        radius_decay: float,
    ):
        """
        Main routine for training an SOM. It requires an initialized SOM grid
        or a partially trained grid as parameter

        :param step_divider:
        :param radius_decay:
        :param sigma:
        :param lr_decay:
        :param epochs:
        :param learn_rate:
        :return:
        """
        radius_sq = round(sigma * pow(self.avg_dim, 2))
        len_train_data = len(self.train_data)
        complexity = epochs * self.width * self.height * len_train_data

        logger.info(f"Complexity: {'{:,}'.format(complexity)}")

        somap = self.get_random_grid()
        logger.info(f"Starting entropy: {self.get_entropy(somap)}")
        rand = np.random.RandomState(0)
        step = self.avg_dim / step_divider
        min_step = 3
        logger.info(f"start with step size: {step}")
        for epoch in range(epochs):
            logger.info(f" epoch {epoch}")
            logger.info(f"Max. surrounding pixels to update per pixel: {pow(step, 2)}")
            rand.shuffle(self.train_data)
            # Update learning rate and radius.
            #  At epoch 0, values will stay identical.
            learn_rate = self.decay_value(learn_rate, lr_decay, epoch + 1)
            radius_sq = self.decay_value(radius_sq, radius_decay, epoch + 1)
            step = round(self.decay_value(step, radius_decay, epoch + 1))

            for i, train_ex in enumerate(self.train_data):
                if i % 500 == 0:
                    logger.info(f"{i}/{len_train_data}...")
                g, h = som_math.find_bmu(somap, train_ex)
                somap = som_math.update_weights(
                    somap, train_ex, learn_rate, radius_sq, (g, h), step=step
                )
            if step < min_step:
                step = min_step
            logger.info(f"Epoch {epoch} entropy: {self.get_entropy(somap)}")
            logger.info(f"updated step: {step}")
        logger.info(f"Final entropy: {self.get_entropy(somap)}")
        return somap

    @staticmethod
    def get_entropy(image: ndarray):
        return grayscale_4bit(Image.fromarray(np.uint8(image))).entropy()

    @staticmethod
    def decay_value(val, decay, epoch) -> float:
        # decay a value to eventually approach zero with a high enough epoch
        return val * np.exp(-epoch * decay)
