import math
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from numpy import ndarray

from main import save_image


class VectorField:
    def __init__(self, range_lo, range_hi, w, h):
        self.w = w
        self.h = h
        # linspace: range_lo, range_hi, data points. distribution is linear.
        self.x, self.y = np.meshgrid(
            np.linspace(range_lo, range_hi, self.w),
            np.linspace(range_lo, range_hi, self.h),
        )
        self.u: Optional[ndarray] = None
        self.v: Optional[ndarray] = None

    def display(self):
        # quiver: plot a field of 2d arrows
        plt.quiver(self.x, self.y, self.u, self.v)
        plt.show()


class FieldAnimation:
    def __init__(self, image: ndarray, field: VectorField = None):
        self.image = image
        self.field = field

    def advance(self):
        new_image = self.image.copy()
        # for each pixel in self.data, apply the vector field
        w = len(self.image)
        h = len(self.image[0])
        for nx, i in enumerate(self.image):
            for ny, j in enumerate(i):
                delta_x = math.floor(self.field.u[nx][ny])
                delta_y = math.floor(self.field.v[nx][ny])
                new_image[(nx + delta_x) % w][(ny + delta_y) % h] = j
        self.image = new_image
        pass


class SimpleImage:
    def __init__(self, w, h):
        with Image.open("input-images/modular-pink-blue-2019.jpeg") as im:
            im = im.convert("RGB")

        # self.data = np.zeros((w, h, 3), dtype=np.uint8)
        self.data = np.array(im)
        # self.data[int(w / 2), int(h / 2)] = [255, 0, 0]

    def display(self):
        plt.imshow(self.data)
        plt.show()


if __name__ == "__main__":
    w = 46
    h = 61

    f = VectorField(-5, 5, w, h)

    # Vector[u, v] cannot produce 0
    f.u = (-f.y / np.sqrt(f.x**2 + f.y**2)) * 2
    f.v = (f.x / np.sqrt(f.x**2 + f.y**2)) * 2

    # f.display()
    s = SimpleImage(w, h)
    animation = FieldAnimation(image=s.data, field=f)
    animation.field = f
    save_image(animation.image, f"im0.png", multires=False)
    # plt.imshow(animation.image)
    # plt.show()
    for i in range(1, 240):
        animation.advance()
        save_image(animation.image, f"im{i}.png", multires=False)
        # plt.imshow(animation.image)
        # plt.show()
    pass
