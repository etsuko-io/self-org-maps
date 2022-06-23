import numpy as np
from PIL import Image

from main import save_image


if __name__ == "__main__":
    path1 = "results/2022-06-17T183700/img_[lr-0.5]_[sigma-42]x3.png"
    path2 = "results/2022-06-17T183700/img_[lr-0.5]_[sigma-84]x3.png"

    with Image.open(path1) as im1:
        im1 = im1.convert("RGBA")

    with Image.open(path2) as im2:
        im2 = im2.convert("RGBA")

    for n in range(0, 96):
        blended = Image.blend(im1, im2, alpha=n / 96)
        save_image(np.array(blended), f"im{n}.png", multires=False)
