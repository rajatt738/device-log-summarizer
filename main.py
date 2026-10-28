"""
Device Log Summarizer CLI Tool
Main entry point orchestrating sanitization testing, data processing, and visualization.
"""

import argparse
import sys
from sanitizer import run_tests as run_sanitizer_tests
from summarizer import process_telemetry_pipeline
from visualizer import generate_temperature_chart


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Device Log Summarizer CLI Tool: Ingests, cleans, summarizes, and visualizes device telemetry."
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="device_telemetry.csv",
        help="Path to the input device telemetry CSV file (default: device_telemetry.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output_summary.json",
        help="Path to save the aggregated JSON output (default: output_summary.json)",
    )
    parser.add_argument(
        "--chart",
        type=str,
        default="temperature_summary.png",
        help="Path to save the generated visualization chart (default: temperature_summary.png)",
    )
    parser.add_argument(
        "--max-temp",
        type=float,
        default=80.0,
        help="Maximum allowed average temperature threshold for devices (default: 80.0)",
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Run only Section 1 sanitization tests and exit.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip Section 1 sanitization tests during full pipeline run.",
    )
    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="Skip Section 3 visualization generation.",
    )

    args = parser.parse_args()

    # Section 1: Sanitizer Unit Tests
    if not args.skip_tests or args.test_only:
        print("[Step 1/3] Validating Section 1 (Sensor Sanitization Logic)...")
        run_sanitizer_tests()
        if args.test_only:
            return

    # Section 2: Core Data Processing & Summarization
    print(f"[Step 2/3] Processing telemetry data from '{args.csv}'...")
    summary = process_telemetry_pipeline(
        csv_path=args.csv,
        output_json_path=args.output,
        max_avg_temp=args.max_temp,
    )

    if not summary:
        print("[Info] No devices passed the criteria or file could not be processed.", file=sys.stderr)
        return

    # Section 3: Visualization Generation
    if not args.no_chart:
        print(f"[Step 3/3] Generating temperature visualization chart to '{args.chart}'...")
        generate_temperature_chart(json_path=args.output, output_image_path=args.chart)

    print("\n[Complete] All pipeline steps executed successfully!\n")


if __name__ == "__main__":
    main()
