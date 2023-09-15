import argparse
import json

from loguru import logger

from src.som.common.models import SomArtBlueprint
from src.som.worker.domains.processor import SomBlueprintProcessor


parser = argparse.ArgumentParser()

parser.add_argument("--blueprint-path")

if __name__ == "__main__":
    logger.info("CLI process started")
    args = parser.parse_args()
    with open(args.blueprint_path, "r") as f:
        # Load the contents of the file as a JSON object
        blueprint = json.load(f)

    blueprint_obj = SomArtBlueprint(**blueprint)
    SomBlueprintProcessor().process(blueprint_obj)
