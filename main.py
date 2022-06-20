import datetime
import math
import os
import random
from functools import lru_cache
from os.path import join

import cv2
import matplotlib.pyplot as plt
import numpy as np
from artefact.artefact import Artefact
from cv2 import dnn_superres
from PIL import Image
from numpy import ndarray
from project.project import Project
from naming.naming import NamingUtil
from pathlib import Path


SYMBOL_ETA = "$\eta$"
SYMBOL_SIGMA_SQ = "$\sigma^2$"


class SelfOrgMap:
    def __init__(self, name, parent_dir):
        self.project = Project(name=name, parent_dir=parent_dir)
        self.project.add_folder("epochs")

    def get_output_path(
        self,
    ):
        now = (
            datetime.datetime.now()
            .replace(microsecond=0, second=0)
            .isoformat()
            .replace(":", "")
        )
        project = now
        dir_path = f"results/{project}"
        os.mkdir(f"results/{project}")
        return dir_path

    # Return the (g,h) index of the BMU in the grid
    def find_bmu(self, somap, x):
        """
        Find the coordinates of the pixel on the SOM grid whose color matches most
         closely to the training pixel.
        """

        # (somap - x): for every pixel in the grid, subtract x
        # This gives the distance [Δr, Δg, Δb] between the training pixel and
        #  each grid pixel.

        # np.square([Δr, Δg, Δb]), squares the distance for each Δr, Δg, Δb
        # So at this point, you have an exaggerated map of distances

        # The .sum(axis=2) adds up the 3 rgb values to a combined
        #  distance value
        dist_sq = (np.square(somap - x)).sum(axis=2)

        # np.argmin() gets element from the list with the smallest distance value;
        #  this pixel is the best-matching-unit (BMU).
        # unravel_index() returns the coordinates of the BMU
        #  on a 2D grid (i.e. their list indices in a 2D list)
        return np.unravel_index(np.argmin(dist_sq, axis=None), dist_sq.shape)

    @lru_cache
    def get_dist_func(self, dist_sq, radius_sq):
        # this one works very well with cache
        # radius = Sigma

        # "brush" function - decides how heavy the brush is to paint with

        # dist_sq = 2, radius_sq = 2 : 0.60
        # dist_sq = 2, radius_sq = 4 : 0.77
        # dist_sq = 2, radius_sq = 6 : 0.84

        # dist_sq = 2, radius_sq = 4 : 0.77
        # dist_sq = 4, radius_sq = 4 : 0.60
        # dist_sq = 6, radius_sq = 4 : 0.47

        # Outcome between 0-1
        # The higher the dist_sq, the lower the outcome
        # The higher the radius, the higher the outcome
        # The outcome determines how much a pixel's weight is adjusted
        # (closer to 1 is more adjustment)
        return np.exp(-dist_sq / 2 / radius_sq)

    def get_weight_change_value(
        self, learn_rate, dist_func, train_ex, current_weight
    ):
        return learn_rate * dist_func * (train_ex - current_weight)

    @lru_cache
    def get_dist_sq(self, i, j, g, h):
        # i - g = distance in pixels between x-axes
        # j - h = distance in pixels between y-axes
        # pythagoras theorem gives distance squared. we don't do the final square
        # root as it's not needed to compare distances.
        return np.square(i - g) + np.square(j - h)

    # Update the weights of the SOM cells when given a single training example
    # and the model parameters along with BMU coordinates as a tuple
    def update_weights(
        self, somap, train_ex, learn_rate, radius_sq, bmu_coord, step=3
    ):
        g, h = bmu_coord
        # if radius is close to zero then only BMU is changed
        if radius_sq < 1e-3:
            somap[g, h, :] += learn_rate * (train_ex - somap[g, h, :])
            return somap
        range_i = range(max(0, g - step), min(somap.shape[0], g + step))
        range_j = range(max(0, h - step), min(somap.shape[1], h + step))
        # Change all cells in a small neighborhood of BMU
        for i in range_i:
            for j in range_j:
                # distance of the current pixel to the BMU
                dist_sq = self.get_dist_sq(i, j, g, h)

                # todo: where does this dist_func come from, what logic based on?
                dist_func = self.get_dist_func(dist_sq, radius_sq)

                # adjust the color to a value in between its current value, and
                # the training example's value
                somap[i, j, :] += self.get_weight_change_value(
                    learn_rate, dist_func, train_ex, somap[i, j, :]
                )
        return somap

    # Main routine for training an SOM. It requires an initialized SOM grid
    # or a partially trained grid as parameter
    def train_somap(
        self,
        somap,
        train_data,
        learn_rate=0.1,
        radius_sq=1,
        lr_decay=0.1,
        radius_decay=0.1,
        epochs=10,
        step=3,
    ):
        rand = np.random.RandomState(0)
        learn_rate_0 = learn_rate
        radius_0 = radius_sq
        for epoch in range(epochs):
            print(f" epoch {epoch}")
            rand.shuffle(train_data)
            for i, train_ex in enumerate(train_data):
                g, h = self.find_bmu(somap, train_ex)
                somap = self.update_weights(
                    somap, train_ex, learn_rate, radius_sq, (g, h), step=step
                )
                # if i % 2 == 0:
                #     save_image(
                #         somap=somap, file_name=f"{current_iter}/epochs/{epoch}/{i}.jpeg"
                #     )
            # Update learning rate and radius

            # np.exp(-epoch * lr_decay) decreases with every epoch, approaching 0
            # np.exp(x) = e^x = 2.718^x
            # because -epoch * lr_decay is negative, the outcome approaches 0.
            # e.g. e^-10 < 0.00005
            learn_rate = learn_rate_0 * np.exp(-epoch * lr_decay)
            radius_sq = radius_0 * np.exp(-epoch * radius_decay)

            variation_folder = self.project.add_folder(
                f"lr-{learn_rate_0}_sigma-{float(radius_0)}"
            )
            res_x3_folder = variation_folder.add_folder("x3")
            res_x9_folder = variation_folder.add_folder("x9")
            artefact = Artefact(name=f"{epoch}.png", data=np.uint8(somap))

            artefact_x3 = artefact.get_superres(3, new_name=f"{epoch}@x3.png")
            artefact_x9 = artefact_x3.get_superres(
                3, new_name=f"{epoch}@x9.png"
            )

            artefact.save(variation_folder)
            artefact_x3.save(res_x3_folder)
            artefact_x9.save(res_x9_folder)

        return somap

    def save_image(self, data: ndarray, file_name, multires=True):
        path = os.path.join(OUT_PATH, file_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im = Image.fromarray(np.uint8(data))
        im.save(path)
        if multires:
            superres = super_res_pillow_img(im, upscale=3)
            superres.save(path.replace(".png", "x3.png"))
            superres2 = super_res_pillow_img(superres, upscale=3)
            superres2.save(path.replace(".png", "x9.png"))

    def train(self, m, n, input_path, epochs, learn_rates, radius_sqs):
        now = datetime.datetime.now()
        print(f"time: {now}")
        with Image.open(input_path) as im:
            im = im.convert("RGB")
            train_data = np.array(im).reshape((-1, 3))

        fig, ax = plt.subplots(
            nrows=len(learn_rates),
            ncols=len(radius_sqs),
            figsize=(20, 20),
            subplot_kw=dict(xticks=[], yticks=[]),
        )
        complexity = (
            epochs
            * img_width
            * img_height
            * len(learn_rates)
            * len(radius_sqs)
            * len(train_data)
        )

        print(f"Complexity: {'{:,}'.format(complexity)}")

        for i, learn_rate in enumerate(learn_rates):
            for j, radius_sq in enumerate(radius_sqs):
                rand = np.random.RandomState(0)
                somap = rand.randint(0, 256, (m, n, 3)).astype(float)
                print(f"Training {i}:{j}...")
                somap = self.train_somap(
                    somap,
                    train_data,
                    epochs=epochs,
                    learn_rate=learn_rate,
                    radius_sq=radius_sq,
                    step=math.ceil(m / 2),
                )
                artefact = Artefact(
                    data=np.uint8(somap),
                    name=f"img_[lr-{learn_rate}]_[sigma-{radius_sq}].png",
                )
                artefact.save(self.project)
                NamingUtil.insert_suffix()
                artefact_x3 = artefact.get_superres(
                    3, new_name=f"{epoch}@x3.png"
                )
                artefact_x9 = artefact_x3.get_superres(
                    3, new_name=f"{epoch}@x9.png"
                )

                txt = (
                    f"{SYMBOL_ETA} = "
                    + str(learn_rate)
                    + f", {SYMBOL_SIGMA_SQ} = "
                    + str(radius_sq)
                    + f", {img_width}x{img_height}px"
                )
                if len(learn_rates) > 1 and len(radius_sqs) > 1:
                    ax[i][j].imshow(somap.astype(int))
                    ax[i][j].title.set_text(txt)
                elif len(learn_rates) > 1 and len(radius_sqs) == 1:
                    ax[i].imshow(somap.astype(int))
                    ax[i].title.set_text(txt)
                elif len(learn_rates) == 1 and len(radius_sqs) > 1:
                    ax[j].imshow(somap.astype(int))
                    ax[j].title.set_text(txt)
                elif len(learn_rates) == 1 and len(radius_sqs) == 1:
                    ax.imshow(somap.astype(int))
                    ax.title.set_text(txt)

        elapsed = round((datetime.datetime.now() - now).seconds / 60, 2)
        num_versions = len(learn_rates) * len(radius_sqs)
        plt.suptitle(
            f"input length = {len(train_data)}, "
            + f"based on {input_path}, "
            + f"epochs = {epochs}, "
            + f"time elapsed = {elapsed} minutes "
            + f", {round(elapsed / num_versions, 2)} minutes per version"
            + f", {round(elapsed / num_versions / epochs, 2)} minutes per epoch"
            + f", complexity = {'{:,}'.format(complexity)}"
        )
        plt.savefig(join(self.project.path, "overview.png"))
        return plt


if __name__ == "__main__":
    som = SelfOrgMap(
        name=NamingUtil.format_iso(NamingUtil.now()),
        parent_dir=Path(__file__).parent.resolve(),
    )

    # Dimensions of the som grid
    img_width = math.ceil(1920 / 9)
    img_height = math.ceil(1080 / 9)
    avg_dim = (img_width + img_height) / 2
    input_path = "input-images/tokyo-station.jpeg"
    epochs = 2
    print(
        f"{epochs} epochs based on {input_path}, @{img_width}x{img_height}px"
    )
    # fmt: off
    learn_rates = [
        0.5,
        0.75,
        0.99,
    ]
    # fmt: on
    radius_sqs = [
        round(avg_dim / 1),
        round(avg_dim / 2),
        round(avg_dim / 4),
        # round(math.pow(avg_dim / 7, 2)),
        # round(math.pow(avg_dim / 3, 2)),
    ]
    print(f"learn rates: {learn_rates}")
    print(f"radius sqs: {radius_sqs}")

    result = som.train(
        img_height,
        img_width,
        input_path=input_path,
        epochs=epochs,
        learn_rates=learn_rates,
        radius_sqs=radius_sqs,
    )

    result.show()
