# mkssubs — Claude Context

## Project purpose

Extract subtitles from `.mks` files and rename them for Jellyfin compatibility. Jellyfin streams external subtitle files (`.srt`, `.sup`, `.ass`, `.idx`/`.sub`) reliably but struggles with `.mks` containers.

## Key files

| File | Purpose |
|---|---|
| `extract_subs.py` | Main extraction script |
| `all_mks_subs_dump.json` | Pre-built mediainfo JSON dump of all `.mks` files |
| `JF_NAMING.md` | Jellyfin external subtitle naming reference |
| `CONTEXT.md` | This file — implementation reference for Claude |

## extract_subs.py — implementation details

### Input

Reads `all_mks_subs_dump.json`, a concatenation of raw `mkvmerge -J` / `mediainfo -F json` JSON objects (one per `.mks` file). The file is not a JSON array; it is parsed with `json.JSONDecoder.raw_decode` in a loop.

### Output filename algorithm

For each subtitle track in each `.mks` file:

1. **Base name** — strip the `.mks` extension from the source path stem. If the stem ends in a known 2-letter IETF language code (e.g. `Movie.en` → strip `.en`), that becomes `base = Movie`. Otherwise the whole stem is the base.

2. **Language** — taken from `language_ietf` property (preferred) or `language` (3-letter fallback), normalized: region stripped (`en-US` → `en`), 3-letter codes mapped to 2-letter (`eng` → `en`).

3. **Flags** — derived from track properties and track name:
   - `forced_track: true` **or** name contains `\bforced\b` (case-insensitive) → `forced`
   - `default_track: true` → `default`
   - name contains `sdh` and does **not** match `\bnon.?sdh\b` → `sdh`
   - name matches `\[cc\]` or `\bcc\b` → `sdh` (CC = closed captions = SDH equivalent in Jellyfin)

4. **Title** — residual meaningful text from the track name after stripping flag/codec/language words (`english`, `pgs`, `srt`, `sdh`, `forced`, `cc`, `bd`, `org`, `eng`, `vobsub`, `ass`, `sub`, `by`, `and`, and all 2-letter IETF language codes). Junk names (`mkvCinemas`, team watermarks) are silently dropped. The result is lowercased, capped at 3 words, and joined with `.`. Unsafe filesystem characters (`/ \ : * ? " < > |`) are removed.

5. **Output stem** — assembled as `{base}.{lang}[.{title}][.{flags...}]`.

6. **Collision resolution** — a per-`.mks`-file dict tracks used stems. If a stem is already taken, `.trackN` (where N is the track id) is appended.

7. **Extension** — `VobSub` → `{stem}.idx` is passed to mkvextract (mkvextract strips the last dot-segment from whatever path it receives, so passing `.idx` makes it strip that and create `{stem}.idx` + `{stem}.sub`); `HDMV PGS` → `.sup`; `SubRip/SRT` → `.srt`; `SubStationAlpha` → `.ass`.

### mkvextract invocation

```
mkvextract tracks <mks_path> <track_id>:<output_path>
```

For VobSub, `output_path` is `{stem}.idx`. mkvextract always strips the last dot-segment from the VobSub output path, so passing `{stem}.idx` causes it to create `{stem}.idx` and `{stem}.sub`. Passing a bare `{stem}` (no extension) would cause mkvextract to strip the last real segment (e.g. `.en` or `.forced`), producing files with the wrong name.

### Output directory

By default, extracted files are written to the same directory as the source `.mks` file. When `--output-dir=<dir>` is passed, `build_plan` prepends the output root to `mks_path.parent`:

```python
out_dir = Path(output_dir) / mks_path.parent
```

This preserves the full relative directory structure under the output root (e.g. `Movies/X/Y/Movie.en.mks` → `output/Movies/X/Y/Movie.en.srt`). The output directory is created with `mkdir(parents=True, exist_ok=True)` just before each `mkvextract` call.

### CLI flags

| Flag | Effect |
|---|---|
| `--execute` | Actually run mkvextract (default is dry-run) |
| `--delete-mks` | Delete `.mks` file after all its tracks extract successfully |
| `--no-skip` | Re-extract even if output file already exists |
| `--output-dir <dir>` | Write extracted files under `<dir>`, preserving relative structure |
| `--skip-redundant-bitmaps` | Drop bitmap tracks (PGS/VobSub) when a text track (SRT/ASS) exists for the same language in the same `.mks` |
| `--skip-codecs=<list>` | Drop entire codec types; comma-separated from `pgs`, `vobsub`, `srt`, `ass`/`ssa` |

Both flags apply in `build_plan` before any extraction, so the dry-run count reflects them. `--skip-codecs` is evaluated first; `--skip-redundant-bitmaps` then applies to whatever bitmap tracks remain. `langs_with_text` is built from all text tracks in the file regardless of `--skip-codecs`, so a file with SRT + PGS will still treat the PGS as redundant even if SRT is also being skipped.

### Known edge cases

- **Multi-language `.mks`** (e.g. Ghajini with ar/nl/fr/he/pt/es tracks) — language is NOT in the `.mks` filename; each track gets its own language code in the output filename.
- **`en-US` language tag** — normalized to `en`.
- **Duplicate tracks with no distinguishing info** (e.g. Terminator 3 has 5 VobSub en tracks, all unnamed) — disambiguated with `.trackN`.
- **SDH commentary tracks** (e.g. Rocky 1976) — get both `.sdh` flag and a short title extracted from the track name.
- **`Non-SDH` track names** — the `\bnon.?sdh\b` guard prevents them from being tagged `.sdh`; they get a title derived from their name instead.
- **VobSub `default_track`** — `default` flag included in the output stem, so mkvextract creates e.g. `Movie.en.default.idx` + `.sub`.
