import datetime

import numpy as np

import som_math


class SingleSom:
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

        print(f"Complexity: {'{:,}'.format(complexity)}")

        now = datetime.datetime.now()
        print(f"time: {now}")
        somap = self.get_random_grid()
        rand = np.random.RandomState(0)
        min_step = 3
        print(f"orig step: {step}")
        for epoch in range(epochs):
            print(f" epoch {epoch}")
            rand.shuffle(self.train_data)
            for i, train_ex in enumerate(self.train_data):
                g, h = som_math.find_bmu(somap, train_ex)
                somap = som_math.update_weights(
                    somap, train_ex, learn_rate, radius_sq, (g, h), step=step
                )
            # Update learning rate and radius
            learn_rate = self.decay_value(learn_rate, lr_decay, epoch)
            radius_sq = self.decay_value(radius_sq, radius_decay, epoch)
            step = round(self.decay_value(step, radius_decay, epoch))
            print(f"updated step: {step}")
        return somap

    @staticmethod
    def decay_value(val, decay, epoch) -> float:
        # decay a value to eventually approach zero with a high enough epoch
        return val * np.exp(-epoch * decay)
