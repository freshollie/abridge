import os
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from unittest.mock import MagicMock, call, create_autospec

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockFixture

import abridge.cli
from abridge.cli import main, _shutdown
from abridge.processor import splice_clip


@pytest.fixture
def mock_threadpool(mocker: MockFixture) -> None:
    mock_class = mocker.patch("abridge.cli.ThreadPoolExecutor")
    mock_instance = create_autospec(ThreadPoolExecutor)()
    mock_instance.__enter__.return_value = mock_instance

    result: Future = Future()
    result.set_result(None)

    mock_instance.submit.return_value = result

    mock_class.return_value = mock_instance

    return mock_class


def test_processes_given_clip(mocker: MockFixture, fs: FakeFilesystem) -> None:
    fs.create_file("testclip.mp4")
    mock_splice_clip = mocker.patch("abridge.processor.splice_clip")

    sys.argv = ["", "testclip.mp4"]

    main()

    mock_splice_clip.assert_called_with("testclip.mp4", "processed", 20, 5)


def test_provides_thresholds(mocker: MockFixture, fs: FakeFilesystem) -> None:
    fs.create_file("testclip.mp4")
    mock_splice_clip = mocker.patch("abridge.processor.splice_clip")

    sys.argv = ["", "-r", "10", "-t", "30", "testclip.mp4"]

    main()

    mock_splice_clip.assert_called_with("testclip.mp4", "processed", 30, 10)


def test_processes_clip_glob(mocker: MockFixture, fs: FakeFilesystem) -> None:
    fs.create_file("testclip.mp4")
    fs.create_file("anotherclip.mp4")
    fs.create_file("thirdclip.mp4")

    mock_splice_clip = mocker.patch("abridge.processor.splice_clip")

    sys.argv = ["", "*.mp4"]

    main()

    mock_splice_clip.assert_has_calls(
        [
            call("testclip.mp4", "processed", 20, 5),
            call("anotherclip.mp4", "processed", 20, 5),
            call("thirdclip.mp4", "processed", 20, 5),
        ],
        any_order=True,
    )


def test_makes_output_directory(mocker: MockFixture, fs: FakeFilesystem) -> None:
    fs.create_file("testclip.mp4")

    mocker.patch("abridge.processor.splice_clip")

    sys.argv = ["", "testclip.mp4", "-o", "outputdir"]

    main()

    os.path.isdir("outputdir")


def test_exits_when_clip_doesnt_exist(mocker: MockFixture, fs: FakeFilesystem) -> None:
    mocker.patch("abridge.processor.splice_clip")

    sys_spy = mocker.spy(abridge.cli, "sys")

    sys.argv = ["", "noexist.mp4", "something.mp4"]

    main()

    sys_spy.exit.assert_called_with(
        "noexist.mp4: No such file or directory\nsomething.mp4: No such file or directory"
    )


def test_exits_when_one_clip_doesnt_exist(
    mocker: MockFixture, fs: FakeFilesystem
) -> None:
    fs.create_file("exists.mp4")
    mocker.patch("abridge.processor.splice_clip")

    sys_spy = mocker.spy(abridge.cli, "sys")

    sys.argv = ["", "exists.mp4", "something.mp4"]

    main()

    sys_spy.exit.assert_called_with("something.mp4: No such file or directory")


def test_doesnt_create_directory_if_clips_error(
    mocker: MockFixture, fs: FakeFilesystem
) -> None:
    mocker.patch("abridge.processor.splice_clip")

    mocker.spy(abridge.cli, "sys")

    sys.argv = ["", "-o", "outputdir", "noexist.mp4"]

    main()

    os.path.isdir("outputdir")


def test_requires_clip() -> None:
    sys.argv = [""]

    with pytest.raises(SystemExit):
        main()


def test_creates_clip_processing_progress(
    mocker: MockFixture, fs: FakeFilesystem
) -> None:
    mock_ui_manager = mocker.patch("abridge.ui._MANAGER")
    mocker.patch("abridge.processor.splice_clip")

    fs.create_file("somefile.mp4")
    fs.create_file("somefile2.mp4")

    sys.argv = ["", "somefile.mp4", "somefile2.mp4"]

    main()

    mock_ui_manager.counter.assert_called_with(
        desc="Processed clips", total=2, unit="clips"
    )


def test_updates_clips_process_bar(mocker: MockFixture, fs: FakeFilesystem) -> None:
    mock_ui_manager = mocker.patch("abridge.ui._MANAGER")
    mocker.patch("abridge.processor.splice_clip")

    fs.create_file("somefile.mp4")
    fs.create_file("somefile2.mp4")

    sys.argv = ["", "somefile.mp4", "somefile2.mp4"]

    main()

    assert mock_ui_manager.counter().update.call_count == 2


def test_threadpool_executes_clips(
    fs: FakeFilesystem, mock_threadpool: MagicMock
) -> None:
    fs.create_file("somefile.mp4")

    sys.argv = ["", "somefile.mp4"]

    main()

    mock_threadpool().submit.assert_called_with(
        splice_clip, "somefile.mp4", "processed", 20, 5
    )


def test_threadpool_sets_workers(
    mocker: MockFixture, fs: FakeFilesystem, mock_threadpool: MagicMock
) -> None:
    mocker.patch("abridge.processor.splice_clip")

    fs.create_file("somefile.mp4")

    sys.argv = ["", "-w", "5", "somefile.mp4"]

    main()

    mock_threadpool.assert_called_with(max_workers=5)


class TestKeyboardInterrupt:
    def test_keyboard_interrupt_shutsdown_pool(
        self, mocker: MockFixture, fs: FakeFilesystem
    ) -> None:
        def mock_splice_clip(*args: int) -> None:
            raise KeyboardInterrupt()

        mocker.patch("abridge.processor.splice_clip", wraps=mock_splice_clip)
        mock_shutdown = mocker.patch("abridge.cli._shutdown")

        fs.create_file("somefile.mp4")
        sys.argv = ["", "somefile.mp4"]

        main()

        mock_shutdown.assert_called()

    def test_shutdown_pool_kills_threads(
        self, mock_threadpool: MagicMock, mocker: MockFixture
    ) -> None:
        mock_concurrent_thread = mocker.patch("abridge.cli.concurrent.futures.thread")
        _shutdown(mock_threadpool)
        mock_threadpool._threads.clear.assert_called()
        mock_concurrent_thread._threads_queues.clear.assert_called()
