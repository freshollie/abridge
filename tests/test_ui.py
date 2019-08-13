from pytest_mock import MockFixture
from typing import Optional
from poshsplice import ui


def mock_update_progress(
    progress_bar: ui.ProgressBar, value: int, old_value: Optional[int] = None
) -> None:
    progress_bar.bars_callback(None, None, value, old_value)


class ProgressBarTest:
    def test_creates_progress_bar_on_initial_update(self, mocker: MockFixture) -> None:
        mock_manager = mocker.patch.object(ui, "_MANAGER", autospec=True)
        progress_bar = ui.ProgressBar("test")

        mock_update_progress(progress_bar, 0)

        mock_manager.counter.assert_called_with(0, 0)
