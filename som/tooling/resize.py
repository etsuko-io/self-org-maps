import base64
import io
import os
from math import ceil, sqrt

from loguru import logger
from PIL import Image


abs_path = "/Users/rubencronie/Dropbox/Documents/Development/self-org-maps/"
file = "input-images/waitress.jpg"


if __name__ == "__main__":
    training_length = 5000

    with Image.open(os.path.join(abs_path, file)) as img:
        current_length = img.width * img.height
        if current_length <= training_length:
            logger.info("Image already at correct size")
            exit(0)

        """
        TL = training_length
        w/x * h/x = TL
        (w*h)/x^2 = TL
        w*h       = TL * x^2
        w*h / TL  = x^2
        x         = sqrt(w*h/TL)

        below, x = scale
        """

        scale = sqrt(current_length / training_length)
        resized = img.resize(
            size=(ceil(img.width / scale), ceil(img.height / scale))
        )
        resized.show()
        img_byte_arr = io.BytesIO()
        resized.save(img_byte_arr, format="PNG")
        img_b64 = base64.b64encode(img_byte_arr.getvalue())

    with open("img-b64.txt", "w") as f:
        f.write(img_b64.decode("utf-8"))
