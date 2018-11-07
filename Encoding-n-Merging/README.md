# n00bscripts - All about mkvmerge & ffmpeg

## Loop template
```bash
#!/bin/bash
for i in *.mkv #Scan all mkv files
do
	i="${i%.mkv}"	#Remove the extension
	<ENTER YOUR COMMAND HERE>
done
```
## MKVMerge - merge audio, chapters.xml, add movie title etc.
```bash
mkvmerge -o "remux_$i.mkv" --language 0:eng --default-track 0:yes --sub-charset 1:UTF-8 --language 1:eng --default-track 1:yes "$i.mkv" --language 0:eng "$i.opus" --title "$name" --chapter-language eng --chapters "$i.chapters.xml" --track-order 0:0,1:0,0:1
```

## MKVMerge - Remove 1 or mode audio tracks
```bash
mkvmerge -o "remux_$i.mkv" -a !2,3 --compression -1:none "$i.mkv"
```

## MKVMerge - Extract Subs/other tracks
```bash
mkvextract tracks "$i.mkv" <TID>:"$i.<ext>"
```
## FFMpeg 720p x265 encoding sweetspot (suggestions welcome)
```bash
ffmpeg-10bit -i "$i.mkv" -map 0 -map_metadata 0 -map_chapters 0 -c copy -c:v libx265 -preset medium -x265-params "crf=25" -pix_fmt yuv420p10le -vf scale=1280:-2 -acodec libopus -af aformat=channel_layouts="7.1|5.1|stereo" -b:a 128k -copy_unknown "Encoded_$i.mkv"
```
