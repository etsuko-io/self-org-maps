from pathlib import Path

import cv2
import numpy as np
from loguru import logger
from PIL import Image
from project_util.project.project import Project


class GraphicsDomain:
    @staticmethod
    def create_blend_animation(
        input_proj: Project,
        output_proj: Project,
        name: str,
        frames_per_blend: int,
    ):
        """
        Blend multiple images into a transitioning animation
        :param name:
        :param output_proj: Project to save animation
        :param input_proj: Project to read images from
        :param project:
        :param frames: number of frames per blend of 2 images
        :return:
        """
        tmp_folder: Project = output_proj.add_folder("_tmp_frames")
        print(f"output path: {output_proj.path}")
        print(f"tmp path: {tmp_folder.path}")

        frames = input_proj.load_images()

        if len(frames) < 2:
            raise ValueError("Not enough images")
        currrent_frame = 0
        last_image = None
        for n, frame in enumerate(frames[: len(frames) - 1]):
            if last_image:
                im1 = last_image
            else:
                im1 = Image.fromarray(frame)
            im2 = Image.fromarray(frames[n + 1])

            for f in range(0, frames_per_blend):
                blended = Image.blend(im1, im2, alpha=f / frames_per_blend)
                as_bgr = cv2.cvtColor(np.array(blended), cv2.COLOR_RGB2BGR)
                tmp_folder.save_image(
                    as_bgr, Path(f"im{currrent_frame:08d}.tiff")
                )
                currrent_frame += 1
        # todo: delete image files?
        logger.info(f"exporting from {tmp_folder.path} to {output_proj.path}")
        codec = "hvc1"
        tmp_folder.export_frames_as_video(
            f"{name}.mp4", target_project=output_proj, codec=codec, fps=25
        )
        print(f"codec = {codec}")
        # hvc1 / .avi works in VLC, quality seems fine
        # hvc1 / .mp4 works in quicktime, quality seems great
