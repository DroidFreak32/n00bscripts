# Usage SplitFlac.sh <cuefile> <flacfile>
shnsplit -f "$1" -t %n-%t -o flac "$2"
cuetag.sh "$1" [0-9]*.flac
