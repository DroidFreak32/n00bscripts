# n00bscripts - All about mkvmerge & ffmpeg & misc Media org stuff

### Loop template
```bash
#!/bin/bash
for i in *.mkv #Scan all mkv files
do
	i="${i%.mkv}"	#Remove the extension
	<ENTER YOUR COMMAND HERE>
done
```
### Cropping bars
```bash
#!/bin/bash

for i in *.mkv #Scan all mkv files
do
	#echo $i > filename.txt
	i="${i%.mkv}"	#Remove the extension
	ffmpeg -i "$i.mkv" -map 0 -map_metadata 0 -map_chapters 0 -c copy -c:v libx265 -preset medium -x265-params crf=24 -pix_fmt yuv420p10le -vf "crop=1920:800:0:140,scale=1280:-2" -acodec libopus -af aformat=channel_layouts="7.1|5.1|stereo" -b:a 128k -copy_unknown ~/Movies/"Encoded_$i.mkv"
	# mkvmerge -o "remux_$i.mkv" "Encoded_$i.mkv" "$i.srt"
	#mv "$i.mkv" ./raw/
done
```
### MKVMerge - merge audio, chapters.xml, add movie title etc.
```bash
mkvmerge -o "remux_$i.mkv" --language 0:eng --default-track 0:yes --sub-charset 1:UTF-8 --language 1:eng --default-track 1:yes "$i.mkv" --language 0:eng "$i.opus" --title "$name" --chapter-language eng --chapters "$i.chapters.xml" --track-order 0:0,1:0,0:1
```

### MKVMerge - Remove 1 or mode audio tracks
```bash
mkvmerge -o "remux_$i.mkv" -a !2,3 --compression -1:none "$i.mkv"
```

### MKVMerge - Only use specific language tracks for audio and subs
```bash
mkvmerge -o output.mkv -s und,eng,jpn -a und,jpn input.mkv
```

### MKVMerge - Extract Subs/other tracks
```bash
mkvextract tracks "$i.mkv" <TID>:"$i.<ext>"
```
### MKVMerge - Set language of a track
Note: Here trackNo is usually 1+trackID found in `mkvmerge -i <filename>`
```bash
mkvpropedit --edit track:<trackNo> --set language=jpn <filename>.mkv
```
### MKVMerge - Batch add title to Videos
```bash
#!/bin/bash
t_array=(
"<TITLE 1>"
"<TITLE 2>"
.
.
"<TITLE n>"
)
index=0
for i in *.mkv #Scan all mkv files (SHOULD BE SORTED ACCORDING TO THE RESPECTIVE TITLE)
do
	i="${i%.mkv}"	#Remove the extension
	mkvpropedit "$i.mkv" --edit info --set "title=${t_array[$((index++))]}"
	# echo "title=${var[$((index++))]}"
done
```
### MKVMerge Reorder Specific tracks and set defaults:
```bash
# Step 1: Identify tracks
$ mkvmerge --identify \[MK-Pn8\]\ Parasyte\ -the\ maxim-\ 01v2\ \[BD\ 1080p\]\[Dual-Audio\]\[E672142C\].mkv
File '[MK-Pn8] Parasyte -the maxim- 01v2 [BD 1080p][Dual-Audio][E672142C].mkv': container: Matroska
Track ID 0: video (MPEG-4p10/AVC/H.264)
Track ID 1: audio (FLAC)
Track ID 2: audio (FLAC)
Track ID 3: subtitles (SubStationAlpha)
Track ID 4: subtitles (SubStationAlpha)
Attachment ID 1: type 'application/x-truetype-font', size 83160 bytes, file name 'DAYROM.ttf'
Attachment ID 2: type 'application/x-truetype-font', size 106728 bytes, file name 'GandhiSans-Bold.otf'
Attachment ID 3: type 'application/x-truetype-font', size 114888 bytes, file name 'GandhiSans-BoldItalic.otf'
Attachment ID 4: type 'application/x-truetype-font', size 135312 bytes, file name 'helvetica-neue-bold.ttf'
Attachment ID 5: type 'application/x-truetype-font', size 33024 bytes, file name 'JandaEverydayCasual.ttf'
Attachment ID 6: type 'application/x-truetype-font', size 38220 bytes, file name 'Kreon-Bold.ttf'
Attachment ID 7: type 'application/x-truetype-font', size 37432 bytes, file name 'Kreon-Regular.ttf'
Attachment ID 8: type 'application/x-truetype-font', size 85276 bytes, file name 'OctemberScript.ttf'
Attachment ID 9: type 'application/x-truetype-font', size 82256 bytes, file name 'Alpha54.ttf'
Attachment ID 10: type 'application/x-truetype-font', size 28624 bytes, file name 'ArtificeSSK.ttf'
Attachment ID 11: type 'application/x-truetype-font', size 77744 bytes, file name 'AVERIASANS-LIGHT.TTF'
Chapters: 6 entries

# Step 2: Reorder and merge
$ mkvmerge -o ../../gd1/ps.mkv -a 2 --default-track 2:true -s 4 --default-track 4:true \[MK-Pn8\]\ Parasyte\ -the\ maxim-\ 01v2\ \[BD\ 1080p\]\[Dual-Audio\]\[E672142C\].mkv

mkvmerge v52.0.0 ('Secret For The Mad') 64-bit
'[MK-Pn8] Parasyte -the maxim- 01v2 [BD 1080p][Dual-Audio][E672142C].mkv': Using the demultiplexer for the format 'Matroska'.
'[MK-Pn8] Parasyte -the maxim- 01v2 [BD 1080p][Dual-Audio][E672142C].mkv' track 0: Using the output module for the format 'AVC/H.264'.
'[MK-Pn8] Parasyte -the maxim- 01v2 [BD 1080p][Dual-Audio][E672142C].mkv' track 2: Using the output module for the format 'FLAC'.
'[MK-Pn8] Parasyte -the maxim- 01v2 [BD 1080p][Dual-Audio][E672142C].mkv' track 4: Using the output module for the format 'text subtitles'.
The file '../../gd1/ps.mkv' has been opened for writing.
```

### FFMpeg 720p x265 encoding sweetspot (suggestions welcome)
```bash
ffmpeg -i "$i.mkv" -map 0 -map_metadata 0 -map_chapters 0 \
	-c copy -c:v libx265 -preset medium -x265-params "crf=25" -pix_fmt yuv420p10le \
	-vf scale=1280:-2 -acodec libopus -af aformat=channel_layouts="7.1|5.1|stereo" -b:a 128k \
	-copy_unknown "Encoded_$i.mkv"
```

### FFMpeg reorder tracks
```bash
ffmpeg -i a.mkv -i b.mkv -map_metadata 0 -map_chapters 0 -map 0:v:0 -map 1:a:0 -map 0:s:0 -map 0:t -c copy -copy_unknown output.mkv
```
This maps the tracks according to the order given in the `-map` option.  
In this case, the tracks will be ordered as:
1) a's video
2) b's *first* audio track only
3) a's subtitles
4) a's attachments

### FFMpeg Replace existing subtitles with new ones (Same file name)
```bash
ffmpeg -i "$i.mkv" -i "$i.srt" -map 0:v -map 0:a -map 1:s -map 0:t? -map_metadata 0 -map_chapters 0 -c copy -copy_unknown "remux_$i.mkv"
rm "$i.mkv" "$i.srt"
```
### Set the timestamp of a video file based on the filename
```bash
for i in *.mp4; do j="${i%.mp4}"; TIME=$(echo $j | sed "s/VID_//g;" | sed "s/_//g;" ) ; TIME="${TIME::-2}"; touch -mt $TIME $i ; done
```

### FFMpeg HWAccel
```bash
ffmpeg -strict 2 -hwaccel auto -i INPUT.mkv -metadata -c:v hevc_nvenc -rc vbr -cq 24 -qmin 24 -qmax 24 -profile:v main10 -preset:v slow -pix_fmt p010le -b:v 0K -bf:v 3 -coder:v cabac -b_ref_mode:v middle -refs:v 16 -c:a copy -c:s copy -map_chapters 0 -map 0 -map_metadata 0 OUTPUT.mkv

### [ReNamer](https://www.den4b.com/products/renamer) rules for Music filename formatting
```text
1) Replace: Replace using wildcards " A " with " a ", " An " with " an ", " The " with " the ", " And " with " and ", " But " with " but ", " Or " with " or ", " On " with " on ", " Nor " with " nor ", " For " with " for ", " From " with " from ", " Yet " with " yet ", " So " with " so ", " As " with " as ", " At " with " at ", " By " with " by ", " In " with " in ", " Of " with " of ", " To " with " to ", " (Album Version)" with "", " (Non-Album Track)" with "", " (Album Version Explicit)" with "", " (Remastered)" with "", ") (Live)" with ")", " Ta " with " ta " (skip extension) (case sensitive)
2) Replace: Replace using wildcards " - t" with " - T", " - i" with " - I", "& t" with "& T", " - a" with " - A", "Come on" with "Come On", "- s" with "- S", "- o" with "- O", "- f" with "- F", "- b" with "- B", "- y" with "- Y" (skip extension) (case sensitive)
3) Remove: Remove using wildcards "Pink Floyd - " (skip extension)
4) Replace: Replace all "[" with "(", "]" with ")", "_" with "" (skip extension)
5) Insert: Insert "Pink Floyd - " as Prefix (skip extension)
```
### Remove excessive padding from flac files
```bash
 find . -type f -name "*flac" -exec metaflac --sort-padding {} \;
 find . -type f -name "*flac" -exec metaflac --remove --block-type=PADDING --dont-use-padding {} \;
```

### Find languages of subtitles/audio present in an MKV file

```bash
mkvmerge --identification-format json --identify Arrival\ \(2016\).mkv | jq -r '.tracks[] | select(.type=="subtitles") | .properties.language'

# Output - Relevant SO link https://stackoverflow.com/a/31911811/6437140
# select(.type=="subtitles") can be changed to select(.type=="audio")

mkvmerge --identification-format json --identify Arrival\ \(2016\).mkv | jq -r '.tracks[] | select(.type=="subtitles") | .properties.language'
eng
eng
ara
chi
cze
dan
dut
est
fin
fre
ger
ger
hun
ice
ita
kor
lav
lit
nob
pol
por
rum
rus
spa
swe
tha
tur
```
