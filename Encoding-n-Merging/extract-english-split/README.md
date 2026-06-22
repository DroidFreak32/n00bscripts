# extract-mkv.sh

One-shot MKV extraction script that separates video/audio/subs and extracts English audio to a standalone file.

## What it does

Given an MKV file with:
- Video + TrueHD Atmos audio + EAC3 audio + non-English audio + subtitles

It produces:
1. **output.mkv** — video + TrueHD audio + English subtitles (SRT preferred, with PGS/VobSub fallback)
2. **output.en.eac3** — standalone English EAC3 audio track (if it exists)

All streams are copied without re-encoding. No intermediate files needed.

If multiple English EAC3 tracks exist, the one with the most channels is selected. If no English EAC3 is found, only the MKV is created.

## Requirements

- `ffmpeg` with ffprobe
- `jq` for JSON parsing

```bash
# macOS
brew install ffmpeg jq

# Ubuntu/Debian
sudo apt install ffmpeg jq

# Fedora/RHEL
sudo dnf install ffmpeg jq
```

## Usage

```bash
chmod +x extract-mkv.sh

# Basic usage (auto-generated output names)
./extract-mkv.sh input.mkv

# Custom output names
./extract-mkv.sh input.mkv custom.mkv custom.en.eac3

# Specify output directory (creates if missing)
./extract-mkv.sh input.mkv -od ./output

# Custom names + output directory
./extract-mkv.sh input.mkv custom.mkv custom.en.eac3 -od ./output
```

### Options

- `-od, --output-dir <dir>` — Create and place outputs in the specified directory

### Output

- `output.mkv` — video + TrueHD + English subs
- `output.en.eac3` — English EAC3 audio only

## How it works

1. **Auto-detects streams** using ffprobe:
   - Video stream (first found)
   - TrueHD audio (required)
   - English EAC3 audio (required)
   - English subtitles (SRT, PGS, or VobSub)

2. **Subtitle fallback chain**:
   - Looks for English SRT subtitles first
   - Falls back to English PGS (HDMV) if no SRT
   - Falls back to English VobSub if no PGS
   - Warns if no English subtitles found

3. **Single ffmpeg command**:
   - Maps selected streams to two outputs
   - Uses `-c copy` (stream copy, no re-encoding)
   - Completes in one pass

## Notes

- Language detection relies on stream language tags. If missing, assumes all tracks are English.
- If multiple English SRT subtitles exist (e.g., SDH + regular), both are included.
- Non-English audio tracks are excluded from the MKV output.
- The script exits with error if required streams (TrueHD, EAC3) are not found.

## Limitations

- Hardcoded to expect TrueHD and EAC3 audio. For different codecs, edit the script to change codec names.
- Assumes first video stream is the one to extract.
- Language detection won't work if stream metadata lacks language tags.

## Example

```bash
$ ./extract-mkv.sh movie.mkv

Analyzing streams in movie.mkv...
✓ Video stream: 0:0
✓ TrueHD audio: 0:1
✓ English EAC3 audio: 0:2
✓ English subtitles: 3 4

Extracting streams...
[ffmpeg output...]

✓ Created: output.mkv (video + TrueHD + subs)
✓ Created: output.en.eac3 (English EAC3)
```
