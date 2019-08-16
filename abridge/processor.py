"""
abridge - an automated video splicing tool
"""

import ntpath
import os
from typing import List, Tuple

import numpy as np
from moviepy.editor import VideoFileClip

from . import ui


def _find_voids(
    clip: VideoFileClip, diff_threshold: float, repetition_threshold: int
) -> List[Tuple[float, float]]:
    cuts: List[Tuple[float, float]] = []
    last_used_frame = None
    last_used_frame_t = 0

    num_similar = 0

    with ui.ProgressBar(f"{clip.filename} - Processing frames", 1) as progress:
        for frame_t, frame in clip.iter_frames(with_times=True, logger=progress):
            if last_used_frame is None:
                last_used_frame = frame
                last_used_frame_t = frame_t
                continue

            diff = np.mean((frame - last_used_frame) ** 2)

            if diff < diff_threshold:
                # there are no signficant differences between this frame and the
                # last used frame

                num_similar += (
                    1  # Count the number of frames in a row which are similar
                )

            else:
                # there was a significant difference between the frames
                if num_similar > repetition_threshold:
                    # there were enough differences in a row
                    cuts.append((last_used_frame_t, frame_t))

                # take note of this frame, and use it as reference for comparison
                last_used_frame = frame
                last_used_frame_t = frame_t
                num_similar = 0

    return cuts


def splice_clip(
    path: str,
    out_dir: str = "processed",
    diff_threshold: float = 20,
    repetition_threshold: int = 5,
) -> None:
    """
    Splice and render out the given clip with the given processing attributes
    """

    clip = VideoFileClip(path)
    clipname = ntpath.basename(path)

    cuts: List[Tuple[float, float]] = _find_voids(
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
