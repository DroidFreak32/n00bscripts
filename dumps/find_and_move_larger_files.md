## [Stack Exchange Link](https://unix.stackexchange.com/a/548754)
### Original script
```bash
PATH_TO_COMPARE="../../TEMP"
for i in *; do
    REF_FILE="$i"
    if [[ -f "$PATH_TO_COMPARE"/$REF_FILE ]]; then
        DUP_FILE="$PATH_TO_COMPARE/$REF_FILE"
        if [[ $(stat -c %s "$REF_FILE") -gt $(stat -c %s "$DUP_FILE") ]]; then
            printf "File %s is larger than %s.\n" "$REF_FILE" "$DUP_FILE"
            ls -alh "$REF_FILE"
            ls -alh "$DUP_FILE"
            mv -vi "$REF_FILE" larger/
            echo
        fi
    fi
done
```

### AI Improved
```bash

#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error when substituting.
# Cause a pipeline to fail if any command fails.
set -euo pipefail

# Define the path to the directory to compare against
PATH_TO_COMPARE="../2020/PRESENT"
# Define the destination directory for larger files
MOVE_DEST_DIR="larger"

# --- Input Validation and Setup ---

# Check if the comparison directory exists and is a directory
if [[ ! -d "$PATH_TO_COMPARE" ]]; then
    echo "Error: Comparison directory '$PATH_TO_COMPARE' does not exist or is not a directory." >&2
    exit 1
fi

# Optional: Create the destination directory if it doesn't exist
# Use -p to avoid error if it already exists and create parent directories if needed
mkdir -p "$MOVE_DEST_DIR"
if [[ ! -d "$MOVE_DEST_DIR" ]]; then
    echo "Error: Failed to create destination directory '$MOVE_DEST_DIR'." >&2
    exit 1
fi

# --- Main Logic ---

# Iterate through all items in the current directory
# Using `*` requires careful handling of filenames (see below)
for ref_file in *; do
    # Skip directories and non-regular files in the current directory
    # The -f check ensures we only process regular files (not directories, links, etc.)
    if [[ ! -f "$ref_file" ]]; then
        continue # Skip to the next item in the loop
    fi

    # Construct the full path to the corresponding file in the comparison directory
    dup_file="$PATH_TO_COMPARE/$ref_file"

    # Check if the corresponding file exists AND is a regular file
    if [[ -f "$dup_file" ]]; then
        # Get file sizes using stat
        # Assigning to variables makes the comparison clearer
        ref_size=$(stat -c %s "$ref_file")
        dup_size=$(stat -c %s "$dup_file")

        # Compare sizes numerically
        # Check if the file in the current directory is strictly larger
        if [[ "$ref_size" -gt "$dup_size" ]]; then
            printf "File '%s' (%s bytes) is larger than '%s' (%s bytes).\n" \
                   "$ref_file" "$ref_size" "$dup_file" "$dup_size"

            # Show details using ls -lh for human-readable sizes
            ls -lh "$ref_file"
            ls -lh "$dup_file"

            # Move the larger file (-v: verbose, -i: interactive/prompt)
            # Use the variable for the destination directory
            echo mv -vi "$ref_file" "$MOVE_DEST_DIR/"

            echo # Add a blank line for better separation
        fi
    fi
done

echo "Script finished."
```
