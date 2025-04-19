#!/usr/bin/env python3
import os
import decimal
import pathlib
import argparse
import json
from datetime import datetime

def get_modification_times_pathlib(path):
    """
    Recursively traverses a directory and retrieves modification times for all files using pathlib.

    Args:
        path: The path to the directory to traverse.

    Returns:
        A dictionary where keys are file paths relative to the input path,
        and values are datetime objects representing the last modification time.
    """
    modification_times = {}
    for file_path in pathlib.Path(path).rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(path)
            modification_times[str(relative_path)] = decimal.Decimal(file_path.stat().st_mtime_ns)/1000000000
    return modification_times

def main():
    parser = argparse.ArgumentParser(description="Traverse a directory and save file modification timestamps.")
    parser.add_argument("path", help="Path to the directory to traverse.")
    parser.add_argument("-o", "--output", default="file_timestamps.json", help="Output JSON file (default: file_timestamps.json)")
    args = parser.parse_args()

    path_to_traverse = args.path
    output_file = args.output

    modification_times = get_modification_times_pathlib(path_to_traverse)

    file_timestamps = {str(path): str(time) for path, time in modification_times.items()}

    with open(output_file, "w") as json_file:
        json.dump(file_timestamps, json_file, indent=4)

    print(f"File modification timestamps saved to {output_file}")

if __name__ == "__main__":
    main()
