#!/bin/bash
# Script to merge video with subtitles with the same index in the file's name.
# Scenario:
# $ ls -1
# > 089 Naming Conventions.mp4 -------------------------------------------------->    089 Naming Conventions.mkv
# > 089-naming-conventions.srt
# > 090 Packages.mp4 ------------------------------------------------------------>    090 Packages.mkv
# > 090-packages.srt
# > 091 Packages Part 2.mp4 ----------------------------------------------------->    091 Packages Part 2.mkv
# > 091-packages-part-2.srt
# > 092 Packages Part 3.mp4 ----------------------------------------------------->    092 Packages Part 3.mkv
# > 092-packages-part-3.srt
# > 093 Packages Challenge Exercise.mp4 ----------------------------------------->    093 Packages Challenge Exercise.mkv
# > 093-packages-challenge-exercise.srt
# > 094 Scope.mp4 --------------------------------------------------------------->    094 Scope.mkv
# > 094-scope.srt
# > 095 Scope Part 2 and Visibility.mp4 ----------------------------------------->    095 Scope Part 2 and Visibility.mkv
# > 095-scope-part-2-and-visibility.srt
# > 096 Scope Challenge Exercise.mp4 -------------------------------------------->    096 Scope Challenge Exercise.mkv
# > 096-scope-challenge-exercise.srt
# > 097 Access Modifiers.mp4 ---------------------------------------------------->    097 Access Modifiers.mkv
# > 097-access-modifiers.srt
# > 098 The static statement.mp4 ------------------------------------------------>    098 The static statement.mkv
# > 098-the-static-statement.srt
# > 099 The final statement.mp4 ------------------------------------------------->    099 The final statement.mkv
# > 099-the-final-statement.srt
# > 100 Final Part 2 and Static Initializers.mp4 -------------------------------->    100 Final Part 2 and Static Initializers.mkv
# > 100-final-part-2-and-static-initializers.srt

for i in *.mp4
do
    FILEBASE="${i%.mp4}"        # Strip the extension
    INDEX="${i:0:3}"            # First three characters of the file
    SRT=`ls $INDEX*.srt`        # Subtitle file has the same index
    echo "Merge :"
    echo "$FILEBASE.mp4 $SRT to"
    echo "$FILEBASE.mkv"
done

echo
echo "Looks good? (y/n)"
read chk
echo

if [ $chk = 'y' -o $chk = 'Y' ]; then
    for i in *.mp4
    do
        FILEBASE="${i%.mp4}"        # Strip the extension
        INDEX="${i:0:3}"            # First three characters of the file
        SRT=`ls $INDEX*.srt`        # Subtitle file has the same index
        ffmpeg -i "$FILEBASE.mp4" -i "$SRT" -map 0 -map 1:0 -map_metadata 0 -map_chapters 0 -c copy -copy_unknown "$FILEBASE.mkv"
        # stream 0 = video, 1=subtitle. map 1:0 = map subtitle stream(1) to video stream(0)
    done
else
    exit 
fi
