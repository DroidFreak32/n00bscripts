# extract-mkv.sh

One-shot MKV extraction script that separates video/audio/subs and extracts English audio to a standalone file.

## What it does

Given an MKV file with multiple audio tracks and subtitles, it extracts:

1. **output.mkv** — video + master audio + English subtitles
   - Master audio priority: TrueHD > DTS-HD > DTS
   - Subtitles: SRT (preferred) → PGS → VobSub
2. **output.en.[codec]** — standalone fallback audio track (if available)
   - Fallback audio priority: EAC3 > AC3 > AAC
   - Extension matches codec: `.eac3`, `.ac3`, or `.aac`
   - If multiple tracks exist, the one with most channels is selected
   - If no fallback audio is found, only the MKV is created

All streams are copied without re-encoding. No intermediate files needed.

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

# Basic usage (output names derived from input)
# Input: movie.2016.2160p.truehd.x265.mkv
# Output: rip-movie.2016.2160p.truehd.x265.mkv + rip-movie.2016.2160p.truehd.x265.en.eac3
# (prefixed with 'rip-' to avoid overwriting the input file)
# (audio extension matches codec: .eac3, .ac3, or .aac)
./extract-mkv.sh movie.2016.2160p.truehd.x265.mkv

# Custom output names (no collision, no prefix)
./extract-mkv.sh input.mkv custom.mkv custom.en

# Specify output directory (creates if missing)
./extract-mkv.sh input.mkv -od ./output

# Custom names + output directory
./extract-mkv.sh input.mkv custom.mkv custom.en -od ./output
```

### Options

- `-od, --output-dir <dir>` — Create and place outputs in the specified directory

### Output

- `output.mkv` — video + TrueHD + English subs
- `output.en.eac3` — English EAC3 audio only

## How it works

1. **Auto-detects master audio** using ffprobe (priority: TrueHD > DTS-HD > DTS):
   - Video stream (first found)
   - Master audio (required)
   - English subtitles (SRT, PGS, or VobSub)

2. **Auto-detects fallback audio** (priority: EAC3 > AC3 > AAC):
   - Optional; if multiple tracks exist, selects the one with most channels
   - Extension automatically matches codec (`.eac3`, `.ac3`, or `.aac`)

3. **Subtitle fallback chain**:
   - Looks for English SRT subtitles first
   - Falls back to English PGS (HDMV) if no SRT
   - Falls back to English VobSub if no PGS
   - Warns if no English subtitles found

4. **Single ffmpeg command**:
   - Maps selected streams to outputs
   - Uses `-c copy` (stream copy, no re-encoding)
   - Completes in one pass

## Notes

- Language detection relies on stream language tags. If missing, assumes all tracks are English.
- If multiple English SRT subtitles exist (e.g., SDH + regular), both are included.
- Non-English audio tracks are excluded from the MKV output.
- Fallback audio is optional; if not found, only the MKV is created.

## Limitations

- Assumes first video stream is the one to extract.
- Language detection won't work if stream metadata lacks language tags.

## Example

```bash
$ ./extract-mkv.sh movie.mkv

Analyzing streams in movie.mkv...
✓ Video stream: 0:0
✓ Master audio (TRUEHD): 0:1
✓ Fallback audio (EAC3): 0:2
✓ English subtitles: 3 4

Extracting streams...
[ffmpeg output...]

✓ Created: output.mkv (video + master audio + subs)
✓ Created: output.en.eac3 (English fallback audio)
```
