"""
Section 2: Core Data Processing Task
Ingests device telemetry CSV, aggregates device statistics,
filters out overheated devices, exports to JSON, and prints a terminal table.
"""

import csv
import json
import math
import os
import sys
from typing import Any, Dict, List, Optional


def load_telemetry_data(csv_file_path: str) -> List[Dict[str, Any]]:
    """
    Reads and validates raw device telemetry from a CSV file.

    Handles edge cases:
    - Missing CSV file
    - Corrupted or unparseable lines
    - Missing required columns
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Input CSV file not found at: '{csv_file_path}'")

    valid_rows: List[Dict[str, Any]] = []

    with open(csv_file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate headers
        required_fields = {"device_id", "status", "temperature"}
        if reader.fieldnames is None or not required_fields.issubset(set(reader.fieldnames)):
            raise ValueError(
                f"CSV must contain headers: {required_fields}. Found: {reader.fieldnames}"
            )

        for line_num, row in enumerate(reader, start=2):
            device_id = (row.get("device_id") or "").strip()
            status = (row.get("status") or "").strip().upper()
            temp_raw = (row.get("temperature") or "").strip()

            if not device_id:
                print(f"[Warning] Skipping row {line_num}: Empty 'device_id'.", file=sys.stderr)
                continue

            try:
                temp_val = float(temp_raw)
            except (ValueError, TypeError):
                print(
                    f"[Warning] Skipping row {line_num}: Invalid temperature '{temp_raw}'.",
                    file=sys.stderr,
                )
                continue

            # Drop NaN temperature values — 'nan' parses as float but corrupts averages
            if not math.isfinite(temp_val):
                print(
                    f"[Warning] Skipping row {line_num}: Non-finite temperature '{temp_raw}'.",
                    file=sys.stderr,
                )
                continue

            valid_rows.append({
                "device_id": device_id,
                "status": status,
                "temperature": temp_val,
            })

    return valid_rows


def aggregate_and_filter(
    records: List[Dict[str, Any]], max_avg_temp: float = 80.0
) -> Dict[str, Dict[str, Any]]:
    """
    Groups telemetry records by device_id and calculates:
    - Total number of records per device
    - Average (mean) temperature
    - Count of records where status is ERROR

    Filters out any devices where average temperature > max_avg_temp (default 80.0).

    Returns:
        Dict[str, Dict[str, Any]]: Filtered aggregation dictionary keyed by device_id.
    """
    # Group raw metrics per device
    grouped_data: Dict[str, Dict[str, Any]] = {}

    for row in records:
        dev_id = row["device_id"]
        if dev_id not in grouped_data:
            grouped_data[dev_id] = {
                "temperatures": [],
                "error_count": 0,
            }

        grouped_data[dev_id]["temperatures"].append(row["temperature"])
        if row["status"] == "ERROR":
            grouped_data[dev_id]["error_count"] += 1

    # Compute statistics and apply filter
    filtered_results: Dict[str, Dict[str, Any]] = {}

    for dev_id, data in grouped_data.items():
        temps = data["temperatures"]
        total_records = len(temps)
        avg_temp = round(sum(temps) / total_records, 2) if total_records > 0 else 0.0

        # Section 2 Requirement: Filter out any devices that have avg temperature > 80.0
        if avg_temp > max_avg_temp:
            continue

        filtered_results[dev_id] = {
            "total_records": total_records,
            "average_temperature": avg_temp,
            "error_count": data["error_count"],
        }

    return filtered_results


def export_to_json(data: Dict[str, Any], output_filepath: str) -> None:
    """
    Saves the aggregated results to a formatted JSON file.
    """
    with open(output_filepath, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"[Export] Aggregated results successfully written to: {output_filepath}")


def print_summary_table(data: Dict[str, Dict[str, Any]]) -> None:
    """
    Prints a formatted ASCII summary table of the aggregated device metrics.
    """
    if not data:
        print("\nNo devices to display (either empty input or all devices exceeded temperature threshold).")
        return

    col_id = "Device ID"
    col_records = "Total Records"
    col_temp = "Avg Temp (°C)"
    col_err = "Error Count"

    header = f"| {col_id:<12} | {col_records:<15} | {col_temp:<15} | {col_err:<12} |"
    separator = "+" + "-" * 14 + "+" + "-" * 17 + "+" + "-" * 17 + "+" + "-" * 14 + "+"

    print("\n" + separator)
    print(header)
    print(separator)

    for dev_id, stats in sorted(data.items()):
        row_str = (
            f"| {dev_id:<12} "
            f"| {stats['total_records']:<15} "
            f"| {stats['average_temperature']:<15.2f} "
            f"| {stats['error_count']:<12} |"
        )
        print(row_str)

    print(separator + "\n")


def process_telemetry_pipeline(
    csv_path: str = "device_telemetry.csv",
    output_json_path: str = "output_summary.json",
    max_avg_temp: float = 80.0,
) -> Dict[str, Dict[str, Any]]:
    """
    Runs the complete Section 2 pipeline: Ingest -> Aggregate -> Filter -> Export -> Print.
    """
    try:
        raw_records = load_telemetry_data(csv_path)
    except FileNotFoundError as e:
        print(f"[Error] {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"[Unexpected Error] Could not process CSV: {e}", file=sys.stderr)
        return {}

    aggregated_data = aggregate_and_filter(raw_records, max_avg_temp=max_avg_temp)
    export_to_json(aggregated_data, output_json_path)
    print_summary_table(aggregated_data)

    return aggregated_data


if __name__ == "__main__":
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "device_telemetry.csv"
    output_json = sys.argv[2] if len(sys.argv) > 2 else "output_summary.json"
    process_telemetry_pipeline(input_csv, output_json)
