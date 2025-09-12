import os
from typing import Any

import pytest

import src.app.config


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
def test_get_debug_mode(debug_mode: Any, expected: bool) -> None:
    os.environ["DEBUG_MODE"] = debug_mode
    assert src.app.config.Configuration.get_debug_mode() is expected
