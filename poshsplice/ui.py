"""
UI components designed to display progress
of processing
"""

from __future__ import annotations

from typing import Any, Optional

import enlighten
from proglog import ProgressBarLogger

_MANAGER = enlighten.get_manager()


def get_manager() -> enlighten.Manager:
    """
    Get the UI manager instance
    """
    return _MANAGER


class ProgressBar(ProgressBarLogger):
    """
    An progress bar which renders the progress of a task
    to the terminal through enlighten. It hooks into
    any function which accepts proglog progress bars
    """

    def __init__(self, description: str, indent_level: int = 0):
        super().__init__()
        self._bar: Optional[enlighten.Counter] = None
        self._desc = description
        self._indent = indent_level

    def _init_bar(self, total: int) -> None:
        self._bar = _MANAGER.counter(
            leave=False,
            total=total,
            desc=f"{self._indent * '  '}{self._desc}",
            unit="frames",
        )

    def bars_callback(
        self, _: Any, __: Any, value: int, old_value: Optional[int] = None
    ) -> None:
        if old_value is None:  # When old_value is none, this is the init value
            self._close()
            self._init_bar(value)

        elif self._bar:
            self._bar.update()

    def callback(self, **kwargs: str) -> None:
        message = kwargs.get("message", None)
        if message:
            print(f"{self._desc} - info: {message}")

    def _close(self) -> None:
        if self._bar:
            self._bar.close(clear=True)

    def __exit__(self, *_: Any) -> None:
        self._close()

    def __enter__(self) -> ProgressBar:
        return self
