# mkssubs — MKS Subtitle Extractor for Jellyfin

Batch-extracts subtitles from `.mks` (Matroska Subtitle) container files and renames them to match Jellyfin's external subtitle naming convention.

## Problem

Jellyfin cannot reliably stream subtitles from `.mks` containers. Raw external subtitle files (`.srt`, `.sup`, `.ass`, `.idx`/`.sub`) work much better.

## Solution

`extract_subs.py` reads the pre-built mediainfo dump (`all_mks_subs_dump.json`), derives the correct Jellyfin-compatible filename for every track in every `.mks` file, and calls `mkvextract` to produce the raw subtitle files in-place.

## Requirements

- Python 3.6+
- `mkvextract` (from the `mkvtoolnix` package)

## Usage

```bash
# Dry-run: see what would be extracted (no files written)
python3 extract_subs.py

# Extract all subtitles
python3 extract_subs.py --execute

# Extract and delete the .mks files afterward
python3 extract_subs.py --execute --delete-mks

# Re-extract even if output files already exist
python3 extract_subs.py --execute --no-skip
```

Default behavior skips tracks whose output file already exists.

## Output naming

Output files are placed in the same directory as the source `.mks` file and named to match the accompanying video file. The naming follows the Jellyfin external subtitle convention (see `JF_NAMING.md`):

```
VideoBaseName.{lang}[.title][.flags].ext
```

| Track property | Filename segment |
|---|---|
| `forced_track: true` or name contains "forced" | `.forced` |
| `default_track: true` | `.default` |
| Name contains "SDH", "CC", or "\[CC\]" | `.sdh` |
| Meaningful track name (e.g. "Commentary 1") | included as title |

### Codec → file extension

| Codec | Extension(s) |
|---|---|
| VobSub | `.idx` + `.sub` |
| HDMV PGS | `.sup` |
| SubRip/SRT | `.srt` |
| SubStationAlpha | `.ass` |

### Examples

| Source track | Output file |
|---|---|
| Single English SRT | `Movie.en.srt` |
| English SRT, forced | `Movie.en.forced.srt` |
| English SRT, SDH | `Movie.en.sdh.srt` |
| English VobSub, forced | `Movie.en.forced.idx` + `.sub` |
| PGS, Commentary | `Movie.en.commentary.sup` |
| Multi-language .mks, Arabic PGS | `Movie.ar.sup` |

When two tracks in the same `.mks` would produce the same output filename, the later one gets `.trackN` appended as a tiebreaker.

## Rebuilding the dump

The dump was produced with:

```bash
find . -name "*.mks" -print0 \
  | xargs -0 -I{} sh -c 'mediainfo -i -F json "{}" | jq -r' \
  > all_mks_subs_dump.json
```

Re-run this if new `.mks` files are added before running the extractor.
