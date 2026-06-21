#!/usr/bin/env python3
"""
Extract subtitles from .mks files with Jellyfin-compatible naming.

Usage:
    python3 extract_subs.py              # dry-run, print what would happen
    python3 extract_subs.py --execute    # actually run mkvextract
    python3 extract_subs.py --execute --delete-mks  # also remove .mks after success
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Codec -> output file extension.
# VobSub is None because mkvextract auto-generates .idx + .sub from base name.
CODEC_EXT = {
    'VobSub': None,
    'HDMV PGS': 'sup',
    'SubRip/SRT': 'srt',
    'SubStationAlpha': 'ass',
}

BITMAP_CODECS = {'VobSub', 'HDMV PGS'}
TEXT_CODECS   = {'SubRip/SRT', 'SubStationAlpha'}

# User-facing codec aliases for --skip-codecs
CODEC_ALIASES = {
    'pgs':    'HDMV PGS',
    'vobsub': 'VobSub',
    'srt':    'SubRip/SRT',
    'ass':    'SubStationAlpha',
    'ssa':    'SubStationAlpha',
}

# Known 2-letter IETF language codes used to detect language suffix in .mks filenames.
LANG_CODES_2 = {
    'en', 'fr', 'de', 'es', 'it', 'ja', 'zh', 'ko', 'pt', 'nl', 'ru',
    'ar', 'hi', 'he', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'hu', 'ro',
    'tr', 'el', 'uk', 'hr', 'sk', 'sl', 'bg', 'lt', 'lv', 'et', 'vi',
    'th', 'id', 'ms', 'fa', 'ur', 'bn', 'ta', 'te', 'ml', 'pa', 'sr',
    'ca', 'eu', 'gl', 'is', 'mt', 'sq', 'af', 'mk', 'bs', 'ga', 'und',
}

# Words stripped from track names when building a title component.
STRIP_WORDS = {
    'english', 'pgs', 'srt', 'ass', 'sub', 'vobsub', 'org', 'eng',
    'bd', 'sdh', 'forced', 'cc', 'by', 'and',
}

# Track names that are purely junk (watermarks, team names, etc.)
JUNK_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r'^mkvcinemas?$',
        r'moviepirate',
        r'^team\s+telly',
        r'^off$',
    ]
]


def parse_json_dump(filepath):
    """Parse a file of concatenated (newline-separated) JSON objects."""
    with open(filepath) as f:
        content = f.read()
    decoder = json.JSONDecoder()
    records = []
    pos = 0
    while pos < len(content):
        chunk = content[pos:].lstrip()
        if not chunk:
            break
        # account for lstrip offset
        lstripped = len(content[pos:]) - len(chunk)
        try:
            obj, end = decoder.raw_decode(chunk)
            records.append(obj)
            pos += lstripped + end
        except json.JSONDecodeError as e:
            print(f"WARNING: JSON parse error at pos {pos}: {e}", file=sys.stderr)
            break
    return records


def normalize_lang(lang_raw):
    """Normalize language tag: en-US -> en, eng -> en (via IETF preferred)."""
    lang = lang_raw.split('-')[0].lower()
    # Map 3-letter codes we might see to 2-letter (mkvmerge usually gives IETF via language_ietf)
    three_to_two = {
        'eng': 'en', 'fra': 'fr', 'deu': 'de', 'spa': 'es', 'ita': 'it',
        'jpn': 'ja', 'zho': 'zh', 'kor': 'ko', 'por': 'pt', 'nld': 'nl',
        'rus': 'ru', 'ara': 'ar', 'hin': 'hi', 'heb': 'he', 'und': 'und',
    }
    return three_to_two.get(lang, lang)


def get_track_lang(track):
    props = track['properties']
    raw = props.get('language_ietf') or props.get('language') or 'und'
    return normalize_lang(raw)


def classify_track(track):
    """Return (flags: list[str], title: str) from a track's properties and name."""
    props = track['properties']
    name = (props.get('track_name') or '').strip()
    name_lower = name.lower()

    is_forced = bool(props.get('forced_track'))
    is_default = bool(props.get('default_track'))
    is_sdh = False

    if re.search(r'\bforced\b', name_lower):
        is_forced = True

    # SDH detection: present unless prefixed by "non-"
    if 'sdh' in name_lower and not re.search(r'\bnon.?sdh\b', name_lower):
        is_sdh = True
    # Closed captions = SDH equivalent
    if re.search(r'\[cc\]|\bcc\b', name_lower):
        is_sdh = True

    title = _extract_title(name)

    flags = []
    if is_default:
        flags.append('default')
    if is_forced:
        flags.append('forced')
    if is_sdh:
        flags.append('sdh')

    return flags, title


def _extract_title(name):
    """
    Derive a Jellyfin title segment from a track name.
    Returns empty string if nothing meaningful remains.
    """
    if not name:
        return ''

    # Reject junk names outright
    for pat in JUNK_PATTERNS:
        if pat.search(name):
            return ''

    # Flatten brackets: (SDH) -> SDH, [CC] -> CC, (#1) -> 1
    n = re.sub(r'[\(\[\{]([^\)\]\}]*)[\)\]\}]', r' \1 ', name)

    # Split on dashes and whitespace
    parts = re.split(r'[-\s]+', n)

    kept = []
    for p in parts:
        p_clean = p.strip('.,;:#')
        pl = p_clean.lower()
        if not pl:
            continue
        if pl in STRIP_WORDS:
            continue
        if pl in LANG_CODES_2:
            continue
        # Pure numbers (like track suffix "#1") and ordinals are usually not meaningful alone
        if pl.isdigit() and len(kept) == 0:
            continue
        kept.append(p_clean)

    result = ' '.join(kept).strip()

    # If the whole thing reduces to nothing or a number, discard
    if not result or result.strip().isdigit():
        return ''

    # Lowercase and replace spaces with dots for filename safety
    result = result.lower()

    # Truncate very long titles (e.g., "SDH - commentary by director...")
    # Keep only up to the first 3 meaningful words
    words = result.split()
    if len(words) > 3:
        result = ' '.join(words[:3])

    # Strip filesystem-unsafe characters, then replace spaces with dots
    result = re.sub(r'[/\\:*?"<>|]', '', result)
    result = result.replace(' ', '.')

    return result


def stem_base(mks_stem):
    """
    Strip a trailing 2-letter language code from the .mks stem.
    e.g. "Movie.en" -> "Movie",  "Film.it" -> "Film",  "NoLang" -> "NoLang"
    """
    parts = mks_stem.rsplit('.', 1)
    if len(parts) == 2 and parts[1].lower() in LANG_CODES_2:
        return parts[0]
    return mks_stem


def build_output_stem(base, lang, flags, title):
    """
    Assemble the output filename stem (no extension).
    Order: base.lang[.title][.flags...]
    """
    parts = [base, lang]
    if title:
        parts.append(title)
    parts.extend(flags)
    return '.'.join(parts)


def build_plan(records, output_dir=None, skip_redundant_bitmaps=False, skip_codecs=None):
    """
    For every track in every .mks file, produce a dict describing the extraction.
    Returns (plan, n_skipped_redundant, n_skipped_codec).

    skip_redundant_bitmaps: drop bitmap tracks when a text track exists for the
                            same language in the same .mks file.
    skip_codecs:            set of internal codec names to drop entirely.
    """
    plan = []
    n_skipped_redundant = 0
    n_skipped_codec = 0

    for rec in records:
        mks_path = Path(rec['file_name'])
        tracks = [t for t in rec.get('tracks', []) if t.get('type') == 'subtitles']

        if not tracks:
            continue

        mks_stem = mks_path.stem                  # e.g. "Movie.en"
        base = stem_base(mks_stem)                # e.g. "Movie"
        if output_dir is not None:
            out_dir = Path(output_dir) / mks_path.parent
        else:
            out_dir = mks_path.parent

        # Languages that have at least one text track in this file (for redundant-bitmap check)
        langs_with_text = {
            get_track_lang(t) for t in tracks if t['codec'] in TEXT_CODECS
        } if skip_redundant_bitmaps else set()

        # Track output stems for collision detection (within this .mks file)
        used_stems = {}

        for track in tracks:
            codec = track['codec']
            track_id = track['id']
            ext = CODEC_EXT.get(codec)

            if codec not in CODEC_EXT:
                print(f"WARNING: unknown codec {codec!r} in {mks_path}, skipping track {track_id}",
                      file=sys.stderr)
                continue

            if skip_codecs and codec in skip_codecs:
                n_skipped_codec += 1
                continue

            lang = get_track_lang(track)

            if skip_redundant_bitmaps and codec in BITMAP_CODECS and lang in langs_with_text:
                n_skipped_redundant += 1
                continue

            flags, title = classify_track(track)

            out_stem = build_output_stem(base, lang, flags, title)

            # Resolve collision by appending track id
            if out_stem in used_stems:
                out_stem = f'{out_stem}.track{track_id}'
            used_stems[out_stem] = track_id

            # Full output path handed to mkvextract:
            # - VobSub: pass {stem}.idx so mkvextract strips .idx and creates
            #   {stem}.idx + {stem}.sub. Without the explicit .idx suffix,
            #   mkvextract strips the last dot-segment of whatever path we give
            #   it (e.g. "Movie.en" → creates "Movie.idx"/"Movie.sub", losing .en).
            # - Others: with extension
            if ext is None:
                mkvextract_out = str(out_dir / f'{out_stem}.idx')
                display_out = f'{out_dir / out_stem}.{{idx,sub}}'
            else:
                mkvextract_out = str(out_dir / f'{out_stem}.{ext}')
                display_out = mkvextract_out

            plan.append({
                'mks_path': str(mks_path),
                'track_id': track_id,
                'codec': codec,
                'lang': lang,
                'flags': flags,
                'title': title,
                'mkvextract_out': mkvextract_out,
                'display_out': display_out,
                'ext': ext,
            })

    return plan, n_skipped_redundant, n_skipped_codec


def check_output_exists(item):
    """Return True if the output file(s) already exist."""
    return Path(item['mkvextract_out']).exists()


def run_plan(plan, execute=False, delete_mks=False, skip_existing=True):
    """Print (dry-run) or execute the extraction plan."""
    if not execute:
        print(f"DRY RUN — {len(plan)} tracks to extract. Pass --execute to run.\n")

    # Group by .mks file for cleaner output
    from itertools import groupby
    key = lambda x: x['mks_path']
    grouped = groupby(sorted(plan, key=key), key=key)

    done = 0
    skipped = 0
    errors = 0
    mks_files_processed = set()

    for mks_path, items in grouped:
        items = list(items)
        print(f"\n{'  ' if execute else ''}[{mks_path}]")

        all_ok = True
        for item in items:
            out = item['display_out']
            prefix = '  '

            if skip_existing and check_output_exists(item):
                print(f"{prefix}SKIP (exists): {out}")
                skipped += 1
                continue

            flags_str = ' '.join(item['flags']) or '-'
            track_info = (f"track {item['track_id']} | {item['codec']} | "
                          f"lang={item['lang']} flags=[{flags_str}] "
                          f"title={item['title']!r}")

            if not execute:
                print(f"{prefix}{track_info}")
                print(f"{prefix}  -> {out}")
                done += 1
                continue

            cmd = ['mkvextract', 'tracks', item['mks_path'],
                   f"{item['track_id']}:{item['mkvextract_out']}"]
            print(f"{prefix}Extracting: {track_info}")
            print(f"{prefix}  -> {out}")
            Path(item['mkvextract_out']).parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{prefix}  ERROR: {result.stderr.strip()}")
                all_ok = False
                errors += 1
            else:
                done += 1

        if execute and all_ok:
            mks_files_processed.add(mks_path)

    print(f"\n{'Extracted' if execute else 'Would extract'}: {done} | "
          f"Skipped: {skipped} | Errors: {errors}")

    if delete_mks and execute:
        print("\nDeleting .mks files...")
        for mks_path in mks_files_processed:
            try:
                os.remove(mks_path)
                print(f"  Deleted: {mks_path}")
            except OSError as e:
                print(f"  ERROR deleting {mks_path}: {e}")


def parse_arg_value(args, flag):
    """Return value for --flag=value or --flag value, or None if absent."""
    for i, arg in enumerate(args):
        if arg.startswith(f'{flag}='):
            return arg.split('=', 1)[1]
        if arg == flag and i + 1 < len(args):
            return args[i + 1]
    return None


def main():
    args = sys.argv[1:]
    execute = '--execute' in args
    delete_mks = '--delete-mks' in args
    skip_existing = '--no-skip' not in args
    skip_redundant_bitmaps = '--skip-redundant-bitmaps' in args

    output_dir = parse_arg_value(args, '--output-dir')

    skip_codecs = set()
    raw_skip = parse_arg_value(args, '--skip-codecs')
    if raw_skip:
        for name in raw_skip.split(','):
            name = name.strip().lower()
            internal = CODEC_ALIASES.get(name)
            if internal:
                skip_codecs.add(internal)
            else:
                print(f"WARNING: unknown codec {name!r}. Valid: {', '.join(sorted(CODEC_ALIASES))}",
                      file=sys.stderr)

    dump_file = 'all_mks_subs_dump.json'
    if not Path(dump_file).exists():
        print(f"ERROR: {dump_file} not found. Run from mkssubs directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {dump_file}...")
    records = parse_json_dump(dump_file)
    print(f"Found {len(records)} .mks files.")

    plan, n_skipped_redundant, n_skipped_codec = build_plan(
        records,
        output_dir=output_dir,
        skip_redundant_bitmaps=skip_redundant_bitmaps,
        skip_codecs=skip_codecs,
    )
    print(f"Planned {len(plan)} track extractions"
          + (f" ({n_skipped_codec} codec-skipped)" if n_skipped_codec else "")
          + (f" ({n_skipped_redundant} redundant-bitmap-skipped)" if n_skipped_redundant else "")
          + ".")
    if output_dir:
        print(f"Output directory: {output_dir}")

    run_plan(plan, execute=execute, delete_mks=delete_mks, skip_existing=skip_existing)


if __name__ == '__main__':
    main()
