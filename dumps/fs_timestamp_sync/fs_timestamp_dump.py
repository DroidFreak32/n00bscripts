import os
import pathlib
from datetime import datetime
import json

# pathlib version
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
    for file_path in pathlib.Path(path).rglob("*"):  # rglob for recursive
        if file_path.is_file():
            relative_path = file_path.relative_to(path)
            modification_times[str(relative_path)] = datetime.fromtimestamp(file_path.stat().st_mtime)
    return modification_times

# Example usage:
path_to_traverse = "/storage/pool/media"  # Replace with the actual path
modification_times = get_modification_times_pathlib(path_to_traverse)

file_timestamps = {}
for relative_path, modification_time in modification_times.items():
    print(f"File: {relative_path}, Modified: {modification_time}")
    file_timestamps[relative_path] = modification_time.timestamp()

with open("file_timestamps.json", "w") as json_file:
    json.dump(file_timestamps, json_file)
