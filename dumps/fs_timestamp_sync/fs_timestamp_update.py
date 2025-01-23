import os
import pathlib
from datetime import datetime
import json

def set_modification_times(path, file_timestamps):
    """
    Recursively traverses a directory and retrieves modification times for all files.

    Args:
        path: The path to the directory to traverse.

    Returns:
        A dictionary where keys are file paths relative to the input path,
        and values are datetime objects representing the last modification time.
    """

    for filename, timestamp in file_timestamps.items():
        full_path = os.path.join(path, filename)
        if not os.path.exists(full_path):
            continue
        if os.path.isfile(full_path):
            print(f"Modifying {full_path} to timestamp: {timestamp}")
            # os.utime(full_path, (timestamp, timestamp))

# Example usage:
path_to_traverse = "/storage/pool/media"  # Replace with the actual path
file_timestamps = {}

with open("file_timestamps.json", "r") as json_file:
    file_timestamps=json.load(json_file)

# print(file_timestamps)
set_modification_times(path_to_traverse, file_timestamps)
