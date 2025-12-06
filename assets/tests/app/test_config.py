import os
from typing import Any

import pytest

import src.app.config


@pytest.fixture
def configuration() -> src.app.config.Configuration:
    return src.app.config.Configuration()


@pytest.mark.parametrize(
    ("debug_mode", "expected"),
    (
        (
            ("True"),
            (True),
        ),
        (
            ("False"),
            (False),
        ),
        (
            ("TRUE"),
            (True),
        ),
        (
            ("FALSE"),
            (False),
        ),
        (
            ("true"),
            (True),
        ),
        (
            ("false"),
            (False),
        ),
        (
            ("Random"),
            (False),
        ),
    ),
)
def test_get_debug_mode(
    configuration: src.app.config.Configuration, debug_mode: Any, expected: bool
) -> None:
    os.environ["DEBUG_MODE"] = debug_mode
    assert configuration.debug_mode is expected


@pytest.mark.parametrize(
    ("app_version", "expected"),
    (
        (
            (None),
            ("Failed to get application version"),
        ),
        (
            ("1.0.0"),
            ("1.0.0"),
        ),
    ),
)
def test_get_app_version(
    configuration: src.app.config.Configuration, app_version: str | None, expected: str
) -> None:
    if app_version is None:
        os.environ.pop("APP_VERSION", None)
    else:
        os.environ["APP_VERSION"] = app_version

    assert configuration.app_version == expected
