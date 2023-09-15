import os

import numpy as np
from matplotlib import pyplot as plt
from numpy import ndarray
from PIL import Image


def entropy(signal: ndarray):
    """
    Function returns entropy of a signal. Signal must be a 1-D numpy array.
    """
    symset = list(set(signal))
    propab = [np.size(signal[signal == i]) / (1.0 * signal.size) for i in symset]
    return np.sum([p * np.log2(1.0 / p) for p in propab])


def grayscale_4bit(im: Image) -> Image:
    """
    Return a 4-bit grayscale version of an image.
    Can be used to reduce color differences in gradients, so that gradients
    are treated as being one colour during entropy calculation.
    :param im:
    :return:
    """
    return im.convert("L").point(lambda x: int(x / 17) * 17)


def image_entropy(file_name, image_caption, image_height, image_width, DPI):
    # source: https://github.com/TamojitSaha/Image_Entropy/blob/master/codex.py
    base = os.path.basename(file_name)
    name = os.path.splitext(base)[0]
    ext = os.path.splitext(base)[1]
    with Image.open(file_name) as color_im:
        grey_im = np.array(grayscale_4bit(color_im))

    N = 5
    S = grey_im.shape
    E = np.array(grey_im)
    for row in range(S[0]):
        for col in range(S[1]):
            Lx = np.max([0, col - N])
            Ux = np.min([S[1], col + N])
            Ly = np.max([0, row - N])
            Uy = np.min([S[0], row + N])
            region = grey_im[Ly:Uy, Lx:Ux].flatten()
            E[row, col] = entropy(region)
    total_entropy = entropy(E.copy().flatten())
    print(f"total entropy: {total_entropy}")
    plt.subplot(1, 3, 3)
    plt.imshow(E, cmap=plt.cm.jet)
    plt.xlabel(image_caption)
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(image_height, image_width)  # in inches
    # when saving, specify the DPI
    new_file_name = "entropy_" + name + ext
    print("\nThe filename is: " + new_file_name)
    plt.savefig(new_file_name, dpi=DPI, bbox_inches="tight")
    # plt.colorbar()
    plt.show()


if __name__ == "__main__":
    # todo: argparse
    abs_path = "/Users/rubencronie/Dropbox/Documents/Development/self-org-maps/"
    # file = "input-images/waitress.jpg"
    file = "results/2022-06-13T145200/img_[lr-0.5]_[sigma-400].jpeg"
    file_name = os.path.join(abs_path, file)
    image_entropy(file_name, "waitress", 10, 8, 300)
