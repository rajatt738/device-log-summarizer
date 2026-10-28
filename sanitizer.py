import math
from typing import Any, List, Optional


def clean_sensor_readings(readings: Optional[List[Any]]) -> List[float]:
    """
    Takes a list of mixed inputs and returns a cleaned list of floats.

    Rules:
    - Drops None values, unconvertible values (e.g. strings like "error"),
      negative values, and non-finite values (NaN, Inf).
    - Clips values above 500.0 to 500.0.
    - Returns [] safely if input is None, empty, or entirely invalid.
    """
    if readings is None or not isinstance(readings, (list, tuple)):
        return []

    result: List[float] = []

    for item in readings:
        if item is None:
            continue

        try:
            val = float(item)
        except (ValueError, TypeError):
            continue

        # float('nan') and float('inf') pass the conversion above without error,
        # but nan comparisons always return False so nan would bypass every filter
        # below and silently end up in the output. isfinite() catches both.
        if not math.isfinite(val):
            continue

        if val < 0.0:
            continue

        if val > 500.0:
            val = 500.0

        result.append(val)

    return result


def run_tests() -> None:
    print("Running Section 1 tests...")

    # Normal mixed input: strings, None, negative, clipping
    sample = [12.5, "45.0", None, -10.0, 550.0, "error_flag", 0, "500.0"]
    expected = [12.5, 45.0, 500.0, 0.0, 500.0]
    result = clean_sensor_readings(sample)
    assert result == expected, f"Test 1 failed: {result}"
    print("[PASS] Test 1: mixed inputs")

    # Edge cases: empty list, None input, all-invalid
    assert clean_sensor_readings([]) == [], "Test 2a failed"
    assert clean_sensor_readings(None) == [], "Test 2b failed"
    assert clean_sensor_readings(["corrupt", None, -99.9, "N/A"]) == [], "Test 2c failed"
    print("[PASS] Test 2: empty / None / all-invalid")

    # Boundary values around 0 and 500
    boundary = [0.0, 499.99, 500.0, 500.01, 1200.0]
    expected_b = [0.0, 499.99, 500.0, 500.0, 500.0]
    result_b = clean_sensor_readings(boundary)
    assert result_b == expected_b, f"Test 3 failed: {result_b}"
    print("[PASS] Test 3: boundary values and clipping")

    # NaN and Infinity — must be dropped, not passed through
    nan_inf = [float("nan"), float("inf"), float("-inf"), 42.0, "nan"]
    result_n = clean_sensor_readings(nan_inf)
    assert result_n == [42.0], f"Test 4 failed: {result_n}"
    print("[PASS] Test 4: NaN and Infinity dropped")

    print("\nAll 4 tests passed.\n")


if __name__ == "__main__":
    run_tests()
