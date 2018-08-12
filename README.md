# n00bscripts
## Replace text from files
	perl -pi -w -e 's/<OLD>/<NEW>/g;' <filename>

Replace `<OLD>` with the current tag and `<NEW>` with the new one

## Recursively Check for missing/corrupted FLAC files
	grep -a -L -r --include="*.flac" "libFLAC"

## Check for files that weren't properly encoded to OPUS
```
# Finds all *.flac files and sends the sorted list to a.txt
find . -name "*.flac" | sort > a.txt

# Using git to commit the file list inorder to do a git diff later. 
git init . ; git add a.txt ; git commit -m "Init"

# Finds all encoded *.opus files, renames the extension to .flac and overwrites a.txt with the new list.
find . -name "*.opus" | sort | sed 's/.opus$/.flac/g;' > a.txt

# The FLAC files which are corrupted are now shown "missing" in the new list (As they couldn't be encoded).
git diff a.txt
```
