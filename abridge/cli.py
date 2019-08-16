"""
CLI module for poshsplice
"""

import argparse
import concurrent.futures.thread
import glob
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from . import __name__ as module_name
from . import processor, ui


def _shutdown(executor: ThreadPoolExecutor) -> None:
    executor._threads.clear()  # type: ignore
    concurrent.futures.thread._threads_queues.clear()


def _runner(args: argparse.Namespace) -> None:
    """
    Run posh splice with the given input args
    """

    clips: List[str] = []
    errors: List[str] = []

    for clip_input in args.clips:
        clip_files = glob.glob(clip_input)
        clips += clip_files

        if not clip_files:
            errors.append(f"{clip_input}: No such file or directory")

    if errors:
        sys.exit("\n".join(errors))

    if not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)

    clips_progress = ui.get_manager().counter(
        desc="Processed clips", unit="clips", total=len(clips)
    )

    with ThreadPoolExecutor(max_workers=args.workers) as executor:

        futures = [
            executor.submit(
                processor.splice_clip,
                clip,
                args.out_dir,
                args.diff_threshold,
                args.repetition_threshold,
            )
            for clip in clips
        ]

        try:
            for future in as_completed(futures):
                future.result()
                clips_progress.update()

        except KeyboardInterrupt:
            _shutdown(executor)

    clips_progress.close()
    ui.get_manager().stop()


def main() -> None:
    """
    CLI main, parse the input args and execute
    """

    parser = argparse.ArgumentParser(
        module_name, description="An automatic clip splicer"
    )
    parser.add_argument(
        "clips", metavar="clip", nargs="+", help="Clip to cut or glob group"
    )
    parser.add_argument(
        "-w",
        default=3,
        type=int,
        metavar="workers",
        help="Number of clip processors",
        dest="workers",
    )
    parser.add_argument(
        "-o", metavar="outdir", type=str, default="processed", dest="out_dir"
    )
    parser.add_argument(
        "-t",
        metavar="diff-threshold",
        type=float,
        default=20,
        dest="diff_threshold",
        help="Difference threshold required between frames for a frames to be considered different",
    )
    parser.add_argument(
        "-r",
        metavar="repetition-threshold",
        type=int,
        default=5,
        dest="repetition_threshold",
        help="Number of frames in a row required to make a cut",
    )

    _runner(parser.parse_args())
