"""
CLI module for poshsplice
"""

import concurrent.futures
import glob
import os

from . import processor, ui


def run(search_str: str = "old/*", out_dir: str = "processed") -> None:
    """
    Run posh splice with the given input args
    """
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    clips = glob.glob(search_str)

    clips_progress = ui.get_manager().counter(
        desc="Processed clips", unit="clips", total=len(clips)
    )

    def clip_processor(clip: str) -> None:
        processor.splice_clip(clip, out_dir)
        clips_progress.update()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(clip_processor, clips)

    except KeyboardInterrupt:
        pass

    clips_progress.close()


def main() -> None:
    """
    CLI main, parse the input args and execute
    """
    run()
