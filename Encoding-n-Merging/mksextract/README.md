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

# Extract all subtitles (in-place, next to each .mks file)
python3 extract_subs.py --execute

# Extract to a separate directory tree (preserving relative structure)
python3 extract_subs.py --execute --output-dir /path/to/output

# Extract and delete the .mks files afterward (only deletes if all tracks extracted successfully)
python3 extract_subs.py --execute --delete-mks

# Re-extract even if output files already exist
python3 extract_subs.py --execute --no-skip

# Skip bitmap tracks (PGS/VobSub) when a text track (SRT/ASS) exists for the same language
python3 extract_subs.py --execute --skip-redundant-bitmaps

# Skip entire codec types (pgs, vobsub, srt, ass)
python3 extract_subs.py --execute --skip-codecs=pgs,vobsub

# Combine: text-only output where possible, no bitmaps at all
python3 extract_subs.py --execute --skip-redundant-bitmaps --skip-codecs=pgs,vobsub
```

Default behavior skips tracks whose output file already exists. Output directories are created automatically when `--output-dir` is used.

### `--delete-mks` with skip flags

`--delete-mks` only deletes a `.mks` file if at least one of its tracks was extracted successfully. The interaction with skip flags:

| Scenario | Deleted? |
|---|---|
| All tracks extracted OK | Yes |
| Any track extraction failed | No |
| `--skip-codecs` filtered out **all** tracks (nothing to extract) | **No** — file never enters the plan |
| `--skip-codecs` filtered some tracks, rest extracted OK | Yes |
| `--skip-redundant-bitmaps`, file has only bitmap tracks (no text fallback) | Yes — bitmaps are not redundant, so they are still extracted |
| `--skip-redundant-bitmaps`, file has SRT + PGS, SRT extracted OK | Yes — PGS is skipped but SRT was extracted |

In short: `--skip-codecs=pgs,vobsub --delete-mks` is safe for bitmap-only `.mks` files — they are skipped entirely and left on disk. `--skip-redundant-bitmaps --delete-mks` will still extract (and then delete) `.mks` files that contain only bitmap tracks with no text alternative.

## Output naming

By default, output files are placed in the same directory as the source `.mks` file. With `--output-dir`, the relative path from the working directory is preserved under the given root — so `Movies/X/Y/Movie.en.mks` extracts to `output/Movies/X/Y/Movie.en.srt`.

Files are named to match the accompanying video file. The naming follows the Jellyfin external subtitle convention (see `JF_NAMING.md`):

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

## TIP: Compressing PGS/VobSub files on BTRFS

Extracted PGS (`.sup`) and VobSub (`.idx`/`.sub`) files can be significantly larger than you might expect. Two reasons:

1. **MKS uses internal zlib compression.** The `.mks` container stores subtitle data compressed. Extraction inflates it back to raw — in this collection that means roughly 2.6× expansion (4.3 GB of `.mks` → ~11 GB extracted).

2. **PGS and VobSub are full-frame bitmaps.** Unlike SRT/ASS which are plain text, these formats store each subtitle line as a full-resolution image. The vast majority of every frame is transparent (empty pixels), which compresses extremely well with general-purpose algorithms — but is stored completely uncompressed on the filesystem after extraction.

SRT and ASS files are already tiny (plain text), so compression is not worth it for those. PGS/VobSub are the ones that benefit.

If you are on BTRFS, you can compress the subtitle files in-place without touching the neighbouring `.mkv` files — BTRFS compression is per-inode, not per-directory:

```bash
find Movies/ TV/ Otaku/ \( -name "*.sup" -o -name "*.idx" -o -name "*.sub" \) \
  -print0 | xargs -0 btrfs filesystem defragment -czstd:3
```

`btrfs filesystem defragment -c<algo>` rewrites each file's extents with the chosen compression. The `.mkv` files next to them are not affected. Run once after extraction; re-run on any newly extracted files.
