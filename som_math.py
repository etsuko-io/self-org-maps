from functools import lru_cache

import numpy as np


@lru_cache
def get_dist_func(dist_sq, radius_sq):
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


def get_weight_change_value(learn_rate, dist_func, train_ex, current_weight):
    return learn_rate * dist_func * (train_ex - current_weight)


@lru_cache
def get_dist_sq(i, j, g, h):
    # i - g = distance in pixels between x-axes
    # j - h = distance in pixels between y-axes
    # pythagoras theorem gives distance squared. we don't do the final square
    # root as it's not needed to compare distances.
    return np.square(i - g) + np.square(j - h)


def find_bmu(somap, x):
    """
    Return the (g,h) index of the BMU in the grid

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


def update_weights(somap, train_ex, learn_rate, radius_sq, bmu_coord, step=3):
    """
    Update the weights of the SOM cells when given a single training example
    and the model parameters along with BMU coordinates as a tuple

    :param somap: the map to update
    :param train_ex: training example to adjust to
    :param learn_rate: how quickly the map should adjust to the training
                        example
    :param radius_sq: the radius in which a single training example can adjust
                        the map
    :param bmu_coord: coordinates of the best-matching-unit on the input map
    :param step: provides a limit to the area of pixels can be adjusted
    :return:
    """
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
            dist_sq = get_dist_sq(i, j, g, h)

            # todo: where does this dist_func come from, what logic based on?
            dist_func = get_dist_func(dist_sq, radius_sq)

            # adjust the color to a value in between its current value, and
            # the training example's value
            somap[i, j, :] += get_weight_change_value(
                learn_rate, dist_func, train_ex, somap[i, j, :]
            )
    return somap
