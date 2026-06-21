# mkssubs — Context

## Project purpose

Extract subtitles from `.mks` files and rename them for Jellyfin compatibility. Jellyfin streams external subtitle files (`.srt`, `.sup`, `.ass`, `.idx`/`.sub`) reliably but struggles with `.mks` containers.

## Key files

| File | Purpose |
|---|---|
| `extract_subs.py` | Main extraction script |
| `all_mks_subs_dump.json` | Pre-built mediainfo JSON dump of all `.mks` files |
| `JF_NAMING.md` | Jellyfin external subtitle naming reference |

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

7. **Extension** — `VobSub` → no extension passed to mkvextract (it auto-creates `.idx` + `.sub`); `HDMV PGS` → `.sup`; `SubRip/SRT` → `.srt`; `SubStationAlpha` → `.ass`.

### mkvextract invocation

```
mkvextract tracks <mks_path> <track_id>:<output_path>
```

For VobSub, `output_path` has no extension; mkvextract creates `output_path.idx` and `output_path.sub`.

### Flags

| Flag | Effect |
|---|---|
| `--execute` | Actually run mkvextract (default is dry-run) |
| `--delete-mks` | Delete `.mks` file after all its tracks extract successfully |
| `--no-skip` | Re-extract even if output file already exists |

### Known edge cases

- **Multi-language `.mks`** (e.g. Ghajini with ar/nl/fr/he/pt/es tracks) — language is NOT in the `.mks` filename; each track gets its own language code in the output filename.
- **`en-US` language tag** — normalized to `en`.
- **Duplicate tracks with no distinguishing info** (e.g. Terminator 3 has 5 VobSub en tracks, all unnamed) — disambiguated with `.trackN`.
- **SDH commentary tracks** (e.g. Rocky 1976) — get both `.sdh` flag and a short title extracted from the track name.
- **`Non-SDH` track names** — the `\bnon.?sdh\b` guard prevents them from being tagged `.sdh`; they get a title derived from their name instead.
- **VobSub `default_track`** — `default` flag included in the output stem, so mkvextract creates e.g. `Movie.en.default.idx` + `.sub`.
