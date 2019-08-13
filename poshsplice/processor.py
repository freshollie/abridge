"""
poshsplice - an automated video splicing tool
"""

import ntpath
import os
from typing import List, Tuple

import numpy as np
from moviepy.editor import VideoFileClip

from . import ui


def _find_voids(
    clip: VideoFileClip, diff_threshold: int, repetition_threshold: int
) -> List[Tuple[int, int]]:
    cuts: List[Tuple[int, int]] = []
    last_frame = None
    last_frame_t = 0

    num_similar = 0

    with ui.ProgressBar(f"{clip.filename} - Processing frames", 1) as progress:
        for frame_t, frame in clip.iter_frames(with_times=True, logger=progress):
            if last_frame is None:
                last_frame = frame
                last_frame_t = frame_t
                continue

            diff = np.mean((frame - last_frame) ** 2)

            if (
                diff < diff_threshold
            ):  # there are no signficant differences in the frames
                num_similar += (
                    1  # Count the number of frames in a row which are similar
                )

            else:  # Something changed
                if num_similar > repetition_threshold:
                    cuts.append((last_frame_t, frame_t))

                last_frame = frame
                last_frame_t = frame_t
                num_similar = 0

    return cuts


def splice_clip(
    path: str,
    out_dir: str = "processed",
    diff_threshold: int = 20,
    repetition_threshold: int = 5,
) -> None:
    """
    Splice and render out the given clip with the given processing attributes
    """

    clip = VideoFileClip(path)
    clipname = ntpath.basename(path)

    cuts: List[Tuple[int, int]] = _find_voids(
        clip, diff_threshold, repetition_threshold
    )

    print(f"{clipname} - Removing empty sections")

    before_time = clip.duration
    for start, end in reversed(cuts):
        clip = clip.cutout(start, end)

    after_time = clip.duration
    print(
        f"{clipname} - Removed {before_time - after_time}s from footage. (before: {before_time}s, after: {after_time}s)"
    )

    with ui.ProgressBar(f"{clipname} - Rendering", 1) as progress:
        clip.write_videofile(
            os.path.join(out_dir, clipname), fps=clip.fps, logger=progress
        )
