from typing import Optional
from unittest import mock

import enlighten
import pytest
from pytest_mock import MockFixture

from abridge import ui


def mock_update_progress(
    progress_bar: ui.ProgressBar, value: int, old_value: Optional[int] = None
) -> None:
    progress_bar.bars_callback(None, None, value, old_value)


@pytest.fixture()
def mock_manager(mocker: MockFixture) -> mock.MagicMock:
    mocked = mocker.patch.object(ui, "_MANAGER", autospec=True)
    mocked.counter.return_value = mock.create_autospec(enlighten.Counter)

    return mocked


class TestProgressBar:
    def test_creates_progress_bar_on_initial_update(
        self, mock_manager: mock.MagicMock
    ) -> None:
        progress_bar = ui.ProgressBar("test_description")

        mock_update_progress(progress_bar, 500)

        mock_manager.counter.assert_called_with(
            desc="test_description", leave=False, total=500, unit="frames"
        )

    def test_updates_counter(self, mock_manager: mock.MagicMock) -> None:
        progress_bar = ui.ProgressBar("test")

        mock_update_progress(progress_bar, 500)
        mock_update_progress(progress_bar, 1, 0)

        assert progress_bar._bar is not None
        progress_bar._bar.update.assert_called()

    def test_creates_new_bar_when_value_resets(
        self, mock_manager: mock.MagicMock
    ) -> None:
        progress_bar = ui.ProgressBar("test")
        mock_update_progress(progress_bar, 500)
        mock_update_progress(progress_bar, 300)

        assert mock_manager.counter.mock_calls == [
            mock.call(desc="test", leave=False, total=500, unit="frames"),
            mock.ANY,
            mock.call(desc="test", leave=False, total=300, unit="frames"),
        ]

    def test_callback_outputs_messages(
        self, mock_manager: mock.MagicMock, mocker: MockFixture
    ) -> None:
        mock_print = mocker.patch("builtins.print")
        progress_bar = ui.ProgressBar("test")
        progress_bar.callback(message="a message")

        mock_print.assert_called_with("test - info: a message")

    def test_callback_does_nothing_with_no_message(
        self, mock_manager: mock.MagicMock, mocker: MockFixture
    ) -> None:
        mock_print = mocker.patch("builtins.print")
        progress_bar = ui.ProgressBar("test")
        progress_bar.callback(somevalue="2")

        mock_print.assert_not_called()

    def test_closes_when_finished(self, mock_manager: mock.MagicMock) -> None:
        progress_bar = ui.ProgressBar("test")
        mock_update_progress(progress_bar, 300)

        with progress_bar:
            pass

        assert progress_bar._bar is not None
        progress_bar._bar.close.assert_called_with(clear=True)


def test_get_manager_returns_manager(mock_manager: mock.MagicMock) -> None:
    manager = ui.get_manager()
    assert manager == mock_manager
