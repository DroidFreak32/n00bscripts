#!/usr/bin/env python3
import os
import decimal
import argparse
import json
from datetime import datetime

def get_existing_mod_times(path):
    """
    Retrieves modification times for all files in the given path.
    """
    existing_times = {}
    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, path)
            existing_times[relative_path] = os.path.getmtime(full_path)
    return existing_times

def set_modification_times(path, file_timestamps, verbosity, actually_update):
    """
    Sets modification times for files based on the provided timestamps, only if they differ.
    """
    existing_times = get_existing_mod_times(path)

    for filename, new_timestamp_str in file_timestamps.items():
        new_timestamp = decimal.Decimal(new_timestamp_str)
        full_path = os.path.join(path, filename)
        if not os.path.exists(full_path):
            if verbosity:
                print(f"VERBOSE: Skipping missing file: {full_path}")
            continue

        if os.path.isfile(full_path):
            current_timestamp = decimal.Decimal(existing_times.get(filename, None))
            if current_timestamp is not None and abs(current_timestamp - new_timestamp) == 0:
                if verbosity:
                    print(f"VERBOSE: Skipping unchanged file: {full_path}")
                continue

            print(f"Updating timestamp for: {full_path} -> {new_timestamp}")
            if actually_update:
                os.utime(full_path, (new_timestamp, new_timestamp))  # Uncomment to apply changes

def main():
    parser = argparse.ArgumentParser(description="Set file modification times from a JSON file.")
    parser.add_argument("path", help="Path to the target directory.")
    parser.add_argument("-i", "--input", default="file_timestamps.json",
                        help="JSON file containing timestamps (default: file_timestamps.json).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-y", "--yes", action="store_true", help="Actually replace the timestamps.")

    args = parser.parse_args()
    verbosity = args.verbose
    actually_update = args.yes

    # Load timestamps from JSON file
    try:
        with open(args.input, "r") as json_file:
            file_timestamps = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: JSON file '{args.input}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{args.input}'.")
        return

    # Set file modification times
    set_modification_times(args.path, file_timestamps, verbosity, actually_update)

if __name__ == "__main__":
    main()
