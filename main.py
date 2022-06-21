import math

from os.path import join

from project_util.naming.naming import NamingUtil
from pathlib import Path

from som import SelfOrgMap

if __name__ == "__main__":
    # Dimensions of the som grid
    img_width = math.ceil(1920 / 30)
    img_height = math.ceil(1080 / 30)
    avg_dim = (img_width + img_height) / 2
    input_path = "input-images/copenhagen.png"
    epochs = 1
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
        # round(math.pow(avg_dim / 7, 2)),
        # round(math.pow(avg_dim / 3, 2)),
    ]
    print(f"learn rates: {learn_rates}")
    print(f"radius sqs: {radius_sqs}")

    som = SelfOrgMap(
        name=f"{NamingUtil.format_iso(NamingUtil.now())}-{NamingUtil.random_name()}",
        parent_dir=join(Path(__file__).parent.resolve(), "results"),
        height=img_height,
        width=img_width,
        input_path=input_path,
        epochs=epochs,
        learn_rates=learn_rates,
        radius_sqs=radius_sqs,
    )

    result = som.train()
    som.show_result(result)
