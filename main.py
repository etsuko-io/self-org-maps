import datetime
import math
from os.path import join
from pathlib import Path

import numpy as np
from PIL import Image
from project_util.artefact.artefact import Artefact
from project_util.naming.naming import NamingUtil
from project_util.project.project import Project
from som import SingleSom

if __name__ == "__main__":
    # Dimensions of the som grid
    img_width = math.ceil(1920 / 18)
    img_height = math.ceil(1080 / 18)
    avg_dim = (img_width + img_height) / 2
    input_path = "input-images/shibuya.png"
    epochs = 5
    print(
        f"{epochs} epochs based on {input_path}, @{img_width}x{img_height}px"
    )
    # fmt: off
    learn_rates = [
        # 0.5,
        0.75,
        0.99,
    ]
    # fmt: on
    radius_sqs = [
        # round(avg_dim / 1),
        round(avg_dim / 2),
        round(avg_dim / 4),
        round(avg_dim / 8),
        # round(math.pow(avg_dim / 7, 2)),
        # round(math.pow(avg_dim / 3, 2)),
    ]
    print(f"learn rates: {learn_rates}")
    print(f"radius sqs: {radius_sqs}")

    """
    todos for structure: 
    - A single instance should actually just be a single map
    - The provided input should be in-memory, not a path
    - What the SOM class returns, should be in-memory, not written anywhere yet
    - Displaying with matplotlib should be optional and separated
    - get_complexity() should be an external method, from an analyzer 
    - make somap.train() return a Somap model that includes metadata 
    """
    with Image.open(input_path) as im:
        im = im.convert("RGB")
        train_data = np.array(im).reshape((-1, 3))

    som_single = SingleSom(
        height=img_height,
        width=img_width,
        train_data=train_data,  # same for multiple variations, so part of init
    )
    proj_name = f"{NamingUtil.format_now()}-{NamingUtil.random_name()}"
    parent_dir = Path(join(Path(__file__).parent.resolve(), "results"))
    proj = Project(name=proj_name, parent_dir=parent_dir)
    # todo: if you want to save individual epochs, you need to return per epoch,
    #  or return a list of epochs
    for lr in learn_rates:
        for sigma in radius_sqs:
            print(f"LR{lr} - R{sigma}")
            result = som_single.train(
                step=math.ceil(avg_dim),
                epochs=epochs,
                learn_rate=lr,
                lr_decay=0.1,
                radius_sq=sigma,
                radius_decay=0.1,
            )
            artefact = Artefact(
                f"img_LR{lr}-R{sigma}.png", project=proj, data=np.uint8(result)
            )
            artefact.save()
            artefact.get_superres(9, new_project=proj.add_folder("x9")).save()
