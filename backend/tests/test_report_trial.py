"""Temporary: deliberate failure to verify the test report (#465). Reverted before review."""


def test_report_trial_failure():
    expected = 3
    assert 1 + 1 == expected, "deliberate failure to verify the test report"
