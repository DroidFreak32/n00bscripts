# Timestamp Sync

This directory contains two Python scripts, They work together to save and restore file modification times. \
Particularly useful to prevent programs like `rclone` form unnecessarily copying files to a remote

### `fs_timestamp_dump.py`:
This script traverses a directory and saves the modification timestamps of all files within that directory (and its subdirectories) to a JSON file.

Parameters:
- `<path_to_directory>`: The directory to traverse.
- `-o <output_file>`: Optional. The name of the output JSON file. Defaults to `file_timestamps.json`.

### `fs_timestamp_update.py`:
This script takes a JSON file (like the one created by `fs_timestamp_dump.py`) and a directory path. It then sets the modification times of the files in the given directory to the timestamps stored in the JSON file. \
It only updates files if the timestamp in the JSON differs from the current file modification time.

Parameters:
- `<path_to_directory>`: The directory whose file timestamps should be updated.
- `-i <input_file>`: Optional. The JSON file containing the timestamps. Defaults to `file_timestamps.json`.
- `-v`: Optional. Verbose mode. Prints messages about skipped files.
## Usage

Workflow:

1. Use fs_timestamp_dump.py to save the current modification times of a directory:
   `python fs_timestamp_dump.py /path/to/my/directory -o timestamps.json`

2. Login to a remote system with identical files and copy over `timestamps.json`

3. Use fs_timestamp_update.py to restore the original modification times from the saved JSON file:
   `python fs_timestamp_update.py /path/to/my/directory -i timestamps.json`

Important: The `fs_timestamp_update.py` script currently prints the intended changes but *does not* actually modify the timestamps.  
To enable the modification, uncomment the line containing `os.utime(full_path, (new_timestamp, new_timestamp))` in the `set_modification_times` function of `fs_timestamp_update.py`.
