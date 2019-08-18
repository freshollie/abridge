import abridge


def test_exports_abridge_clip_directly() -> None:
    assert abridge.abridge_clip == abridge.processor.abridge_clip
