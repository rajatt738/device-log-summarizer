"""
Section 3: Device Temperature Visualizer
Loads aggregated JSON data from Section 2 and generates a
bar chart comparing average temperatures across devices using matplotlib.
"""

import json
import os
import sys
from typing import Dict, Any
import matplotlib.pyplot as plt


def generate_temperature_chart(
    json_path: str = "output_summary.json",
    output_image_path: str = "temperature_summary.png",
) -> None:
    """
    Loads JSON summary and plots a styled bar chart of average temperatures.

    Handles edge cases:
    - Missing JSON file
    - Empty device records
    - Ensures clean layout without overlapping labels or clipped borders.
    """
    if not os.path.exists(json_path):
        print(f"[Error] JSON file '{json_path}' not found. Run Section 2 first.", file=sys.stderr)
        return

    try:
        with open(json_path, mode="r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to parse JSON file '{json_path}': {e}", file=sys.stderr)
        return

    if not data:
        print("[Warning] No device records found in JSON to plot.", file=sys.stderr)
        return

    # Extract device IDs and their respective average temperatures
    device_ids = list(data.keys())
    avg_temperatures = [data[dev]["average_temperature"] for dev in device_ids]

    # Create figure with high DPI and readable aspect ratio
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # Use matplotlib's built-in tab10 colormap so any number of devices (up to 10)
    # gets a distinct color. The old hardcoded 5-color list would silently give fewer
    # colors than bars if more than 5 devices were present.
    # Note: plt.get_cmap() is the correct API in matplotlib 3.x; plt.cm.get_cmap() was removed.
    cmap = plt.get_cmap("tab10")
    bar_colors = [cmap(i) for i in range(len(device_ids))]
    bars = ax.bar(
        device_ids,
        avg_temperatures,
        color=bar_colors,
        width=0.55,
        edgecolor="#1a202c",
        linewidth=1.2,
        zorder=3,
    )

    # Add numeric labels on top of each bar for immediate readability
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.2f}°C",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),  # 5 points vertical offset
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#2d3748",
        )

    # Add title and axis labels
    ax.set_title("Average Temperature per Device", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Device ID", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_ylabel("Average Temperature (°C)", fontsize=11, fontweight="bold", labelpad=10)

    # Add horizontal grid lines for ease of comparison
    ax.yaxis.grid(True, linestyle="--", alpha=0.6, zorder=0)
    ax.set_axisbelow(True)

    # Set appropriate Y-axis limits with headroom for value annotations
    max_temp = max(avg_temperatures) if avg_temperatures else 100
    ax.set_ylim(0, max_temp * 1.18)

    # Ensure layout doesn't clip titles or axis labels
    plt.tight_layout()

    # Save chart to disk
    plt.savefig(output_image_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"[Chart] Temperature summary bar chart saved to: '{output_image_path}'")


if __name__ == "__main__":
    input_json = sys.argv[1] if len(sys.argv) > 1 else "output_summary.json"
    output_png = sys.argv[2] if len(sys.argv) > 2 else "temperature_summary.png"
    generate_temperature_chart(input_json, output_png)
