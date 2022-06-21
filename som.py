import datetime
import math

import som_math
from os.path import join

import matplotlib.pyplot as plt
import numpy as np
from project_util.artefact.artefact import Artefact
from PIL import Image
from project_util.project.project import Project
from project_util.naming.naming import NamingUtil

from constants import SYMBOL_ETA, SYMBOL_SIGMA_SQ


class SelfOrgMap:
    def __init__(
        self,
        name,
        parent_dir,
        width,
        height,
        input_path,
        epochs,
        learn_rates,
        radius_sqs,
    ):
        self.project = Project(name=name, parent_dir=parent_dir)
        self.width = width
        self.height = height
        self.input_path = input_path
        self.epochs = epochs
        self.learn_rates = learn_rates
        self.radius_sqs = radius_sqs
        with Image.open(self.input_path) as im:
            im = im.convert("RGB")
            self.train_data = np.array(im).reshape((-1, 3))
        self.complexity = self.get_complexity()

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
                dist_sq = som_math.get_dist_sq(i, j, g, h)

                # todo: where does this dist_func come from, what logic based on?
                dist_func = som_math.get_dist_func(dist_sq, radius_sq)

                # adjust the color to a value in between its current value, and
                # the training example's value
                somap[i, j, :] += som_math.get_weight_change_value(
                    learn_rate, dist_func, train_ex, somap[i, j, :]
                )
        return somap

    def train_somap(
        self,
        somap,
        learn_rate=0.1,
        radius_sq=1,
        lr_decay=0.1,
        radius_decay=0.1,
        step=3,
    ):
        """
        Main routine for training an SOM. It requires an initialized SOM grid
        or a partially trained grid as parameter

        :param somap:
        :param learn_rate:
        :param radius_sq:
        :param lr_decay:
        :param radius_decay:
        :param step:
        :return:
        """
        rand = np.random.RandomState(0)
        learn_rate_0 = learn_rate
        radius_0 = radius_sq
        for epoch in range(self.epochs):
            print(f" epoch {epoch}")
            rand.shuffle(self.train_data)
            for i, train_ex in enumerate(self.train_data):
                g, h = som_math.find_bmu(somap, train_ex)
                somap = self.update_weights(
                    somap, train_ex, learn_rate, radius_sq, (g, h), step=step
                )
            # Update learning rate and radius

            # np.exp(-epoch * lr_decay) decreases with every epoch, approaching 0
            # np.exp(x) = e^x = 2.718^x
            # because -epoch * lr_decay is negative, the outcome approaches 0.
            # e.g. e^-10 < 0.00005
            learn_rate = learn_rate_0 * np.exp(-epoch * lr_decay)
            radius_sq = radius_0 * np.exp(-epoch * radius_decay)

            epoch_folder = self.project.add_folder(
                f"lr-{learn_rate_0}_sigma-{float(radius_0)}-epochs"
            )
            res_x3_folder = epoch_folder.add_folder("x3")
            res_x9_folder = epoch_folder.add_folder("x9")
            artefact = Artefact(name=f"epoch{epoch}.png", data=np.uint8(somap))

            artefact_x3 = artefact.get_superres(3, new_name=f"{epoch}@x3.png")
            artefact_x9 = artefact_x3.get_superres(
                3, new_name=f"{epoch}@x9.png"
            )

            artefact.save(epoch_folder)
            artefact_x3.save(res_x3_folder)
            artefact_x9.save(res_x9_folder)

        return somap

    def get_complexity(self):
        complexity = (
            self.epochs
            * self.width
            * self.height
            * len(self.learn_rates)
            * len(self.radius_sqs)
            * len(self.train_data)
        )

        print(f"Complexity: {'{:,}'.format(complexity)}")
        return complexity

    def train(self):
        now = datetime.datetime.now()
        print(f"time: {now}")
        result = dict(variations=[])

        for i, learn_rate in enumerate(self.learn_rates):
            for j, radius_sq in enumerate(self.radius_sqs):
                rand = np.random.RandomState(0)
                somap = rand.randint(
                    0, 256, (self.width, self.height, 3)
                ).astype(float)
                print(f"Training {i}:{j}...")
                somap = self.train_somap(
                    somap,
                    learn_rate=learn_rate,
                    radius_sq=radius_sq,
                    step=math.ceil(self.width / 2),
                )
                self.save_variation(somap, learn_rate, radius_sq)
                result["variations"].append(
                    dict(
                        i=i,
                        j=j,
                        data=somap.copy().astype(int),
                        learn_rate=learn_rate,
                        radius_sq=radius_sq,
                    )
                )

        result["elapsed"] = round(
            (datetime.datetime.now() - now).seconds / 60, 2
        )
        return result

    def save_variation(self, somap, learn_rate, sigma):
        artefact = Artefact(
            name=f"img_[lr-{learn_rate}]_[sigma-{sigma}].png",
            project=self.project,
            data=np.uint8(somap),
        )
        artefact.save()
        artefact_x3 = artefact.get_superres(
            3, new_name=NamingUtil.insert_suffix(artefact.name, "@x3")
        )
        artefact_x9 = artefact_x3.get_superres(
            3, new_name=NamingUtil.insert_suffix(artefact.name, "@x9")
        )
        artefact.save()
        artefact_x3.save(self.project)
        artefact_x9.save(self.project)

    def show_result(self, result):
        num_versions = len(self.learn_rates) * len(self.radius_sqs)
        elapsed = result.pop("elapsed")
        fig, ax = plt.subplots(
            nrows=len(self.learn_rates),
            ncols=len(self.radius_sqs),
            figsize=(20, 20),
            subplot_kw=dict(xticks=[], yticks=[]),
        )
        for variation in result["variations"]:
            learn_rate = variation["learn_rate"]
            radius_sq = variation["radius_sq"]
            somap = variation["data"]
            i = variation["i"]
            j = variation["j"]
            txt = (
                f"{SYMBOL_ETA} = "
                + str(learn_rate)
                + f", {SYMBOL_SIGMA_SQ} = "
                + str(radius_sq)
                + f", {self.width}x{self.height}px"
            )

            if len(self.learn_rates) > 1 and len(self.radius_sqs) > 1:
                ax[i][j].imshow(somap.astype(int))
                ax[i][j].title.set_text(txt)
            elif len(self.learn_rates) > 1 and len(self.radius_sqs) == 1:
                ax[i].imshow(somap.astype(int))
                ax[i].title.set_text(txt)
            elif len(self.learn_rates) == 1 and len(self.radius_sqs) > 1:
                ax[j].imshow(somap.astype(int))
                ax[j].title.set_text(txt)
            elif len(self.learn_rates) == 1 and len(self.radius_sqs) == 1:
                ax.imshow(somap.astype(int))
                ax.title.set_text(txt)

        plt.suptitle(
            f"input length = {len(self.train_data)}, "
            + f"based on {self.input_path}, "
            + f"epochs = {self.epochs}, "
            + f"time elapsed = {elapsed} minutes "
            + f", {round(elapsed / num_versions, 2)} minutes per version"
            + f", {round(elapsed / num_versions / self.epochs, 2)} minutes per epoch"
            + f", complexity = {'{:,}'.format(self.get_complexity())}"
        )
        plt.savefig(join(self.project.path, "overview.png"))
        return plt
