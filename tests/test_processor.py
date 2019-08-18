from __future__ import annotations
from unittest.mock import MagicMock, NonCallableMagicMock, call, create_autospec, ANY

import pytest
from pytest_mock import MockFixture

from abridge.processor import abridge_clip, _apply_cuts, _find_voids
from moviepy.editor import VideoFileClip
import os

from typing import List, Tuple, Optional


@pytest.fixture
def mock_video_clip(mocker: MockFixture) -> MagicMock:
    mock_video_clip: MagicMock = mocker.patch(
        "abridge.processor.VideoFileClip", create_autospec=True
    )
    mock_video_clip().duration = 10

    return mock_video_clip


class CuttableVideoClip(VideoFileClip):
    """
    Video clip mock used to test cuting out sections
    of a video
    """

    def __init__(self, cuts: Optional[List[Tuple[float, float]]] = None):
        if not cuts:
            cuts = []
        self._cuts: List[Tuple[float, float]] = cuts

    def cutout(self, start: float, end: float) -> CuttableVideoClip:
        return CuttableVideoClip(self._cuts + [(start, end)])

    def get_cuts(self) -> List[Tuple[float, float]]:
        return self._cuts


class TestApplyCuts:
    def test_applies_cuts_in_reverse_order_on_clip(self) -> None:
        mock_clip = CuttableVideoClip()

        output_clip: CuttableVideoClip = _apply_cuts(
            mock_clip, [(0, 2.3), (5.3, 6), (6.4, 8)]
        )

        assert output_clip.get_cuts() == [(6.4, 8), (5.3, 6), (0, 2.3)]


class TestAbridgeClip:
    def test_loads_clip_from_given_path(
        self, mocker: MockFixture, mock_video_clip: MagicMock
    ) -> None:
        mocker.patch("abridge.processor._find_voids", autospec=True)

        abridge_clip("clippath")

        mock_video_clip.assert_called_with("clippath")

    def test_calculates_cuts_for_clip(
        self, mocker: MockFixture, mock_video_clip: MagicMock
    ) -> None:
        mock_find_voids: MagicMock = mocker.patch(
            "abridge.processor._find_voids", autospec=True
        )
        mock_find_voids.return_value = []
        mock_clip_instance = mock_video_clip()

        abridge_clip("clippath")
        mock_find_voids.assert_called_with(mock_clip_instance, 20, 5)

    def test_applys_cuts_on_given_clip(
        self, mocker: MockFixture, mock_video_clip: MagicMock
    ) -> None:
        mock_find_voids: MagicMock = mocker.patch(
            "abridge.processor._find_voids", autospec=True
        )
        mock_find_voids.return_value = [(0, 2.3), (5.3, 6), (6.4, 8)]

        mock_apply_cuts: MagicMock = mocker.patch(
            "abridge.processor._apply_cuts", autospec=True
        )

        mock_clip_instance: NonCallableMagicMock = mock_video_clip()

        abridge_clip("clippath")

        mock_apply_cuts.assert_called_with(
            mock_clip_instance, [(0, 2.3), (5.3, 6), (6.4, 8)]
        )

    def test_writes_video_clip_with_cuts(
        self, mocker: MockFixture, mock_video_clip: MagicMock
    ) -> None:
        mock_find_voids: MagicMock = mocker.patch(
            "abridge.processor._find_voids", autospec=True
        )

        mock_cut_video = NonCallableMagicMock(VideoFileClip)
        mock_cut_video.duration = 10

        mock_apply_cuts: MagicMock = mocker.patch(
            "abridge.processor._apply_cuts", autospec=True
        )
        mock_apply_cuts.return_value = mock_cut_video

        abridge_clip("clipdir/clip.something", "outpath")

        mock_cut_video.write_videofile.assert_called_with(
            os.path.join("outpath", "clip.something"), logger=ANY
        )
