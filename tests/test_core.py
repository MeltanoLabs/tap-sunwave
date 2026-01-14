"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from singer_sdk.testing import get_tap_test_class

from tap_sunwave.tap import TapSunwave

TestTapSunwave = get_tap_test_class(
    TapSunwave,
    include_tap_tests=False,
    include_stream_tests=False,
    include_stream_attribute_tests=False,
)
