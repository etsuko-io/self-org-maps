from typing import List

from loguru import logger
from transloadit import client


def create_steps(images: List, fps: float, aws_creds: str):
    tl = client.Transloadit("YOUR_TRANSLOADIT_KEY", "YOUR_TRANSLOADIT_SECRET")
    assembly = tl.new_assembly()

    # Set Encoding Instructions
    assembly.add_step(":original", "/upload/handle", {})

    for image_data in images:
        assembly.add_step(
            image_data["name"],
            "/http/import",
            {"result": True, "url": image_data["url"]},
        )

    assembly.add_step(
        "merged",
        "/video/merge",
        {
            "use": {
                "steps": [
                    {"name": ":original", "as": "audio"},
                    {"name": "resized", "as": "image"},
                ],
                "bundle_steps": True,
            },
            "result": True,
            "duration": 9,
            "ffmpeg_stack": "v4.3.1",
            "framerate": fps,
            "preset": "ipad-high",
            "resize_strategy": "fit",
        },
    )
    assembly.add_step(
        "exported",
        "/s3/store",
        {
            "use": [
                "imported_chameleon",
                "imported_prinsengracht",
                "imported_snowflake",
                "resized",
                "merged",
                ":original",
            ],
            "credentials": aws_creds,
            "url_prefix": "https://demos.transloadit.com/",
        },
    )

    # Start the Assembly
    assembly_response = assembly.create(retries=5, wait=True)

    logger.info(assembly_response.data.get("assembly_ssl_url"))
