import numpy as np
from loguru import logger

from som.domains.som import som_math


class SomDomain:
    def __init__(
        self,
        width,
        height,
        train_data,
    ):
        self.width = width
        self.height = height
        self.train_data = train_data

    def get_random_grid(self):
        rand = np.random.RandomState(0)
        somap = rand.randint(0, 256, (self.height, self.width, 3)).astype(
            float
        )
        return somap

    def train(
        self,
        step,
        epochs,
        learn_rate,
        lr_decay,
        radius_sq,
        radius_decay,
    ):
        """
        Main routine for training an SOM. It requires an initialized SOM grid
        or a partially trained grid as parameter

        :param radius_sq:
        :param lr_decay:
        :param epochs:
        :param learn_rate:
        :param somap:
        :param step:
        :return:
        """
        complexity = epochs * self.width * self.height * len(self.train_data)

        logger.info(f"Complexity: {'{:,}'.format(complexity)}")

        somap = self.get_random_grid()
        rand = np.random.RandomState(0)
        min_step = 3
        logger.info(f"start with step size: {step}")
        for epoch in range(epochs):
            logger.info(f" epoch {epoch}")
            rand.shuffle(self.train_data)
            # Update learning rate and radius.
            #  At epoch 0, values will stay identical.
            learn_rate = self.decay_value(learn_rate, lr_decay, epoch)
            radius_sq = self.decay_value(radius_sq, radius_decay, epoch)
            step = round(self.decay_value(step, radius_decay, epoch))

            for i, train_ex in enumerate(self.train_data):
                g, h = som_math.find_bmu(somap, train_ex)
                somap = som_math.update_weights(
                    somap, train_ex, learn_rate, radius_sq, (g, h), step=step
                )
            if step < min_step:
                step = min_step
            logger.info(f"updated step: {step}")
        return somap

    @staticmethod
    def decay_value(val, decay, epoch) -> float:
        # decay a value to eventually approach zero with a high enough epoch
        return val * np.exp(-epoch * decay)
