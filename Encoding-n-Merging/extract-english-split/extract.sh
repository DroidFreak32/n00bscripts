#!/bin/bash
set -e

INPUT=""
OUTPUT_MKV="output.mkv"
OUTPUT_EAC3="output.en.eac3"
OUTPUT_DIR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -od|--output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    -*)
      echo "Unknown option: $1"
      exit 1
      ;;
    *)
      if [ -z "$INPUT" ]; then
        INPUT="$1"
      elif [ "$OUTPUT_MKV" = "output.mkv" ]; then
        OUTPUT_MKV="$1"
      else
        OUTPUT_EAC3="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$INPUT" ]; then
  echo "Usage: $0 <input.mkv> [output.mkv] [output.en.eac3] [-od|--output-dir <dir>]"
  exit 1
fi

# Create output directory if specified
if [ -n "$OUTPUT_DIR" ]; then
  mkdir -p "$OUTPUT_DIR"
  OUTPUT_MKV="$OUTPUT_DIR/$OUTPUT_MKV"
  OUTPUT_EAC3="$OUTPUT_DIR/$OUTPUT_EAC3"
fi

if [ ! -f "$INPUT" ]; then
  echo "Error: Input file not found: $INPUT"
  exit 1
fi

echo "Analyzing streams in $INPUT..."

# Parse streams using ffprobe + jq
STREAMS=$(ffprobe -v error -print_format json -show_streams "$INPUT")

# Get video stream
VIDEO=$(echo "$STREAMS" | jq -r '.streams[] | select(.codec_type=="video") | .index' | head -1)

if [ -z "$VIDEO" ]; then
  echo "Error: No video stream found"
  exit 1
fi

echo "✓ Video stream: 0:$VIDEO"

# Get TrueHD audio stream
TRUEHD=$(echo "$STREAMS" | jq -r '.streams[] | select(.codec_type=="audio" and .codec_name=="truehd") | .index' | head -1)

if [ -z "$TRUEHD" ]; then
  echo "Error: No TrueHD audio found"
  exit 1
fi

echo "✓ TrueHD audio: 0:$TRUEHD"

# Get English EAC3 audio (pick the one with most channels if multiple exist)
EAC3=$(echo "$STREAMS" | jq -r '.streams[] | select(.codec_type=="audio" and .codec_name=="eac3" and (.tags.language=="eng" or .tags.language==null or .tags.language=="")) | "\(.index),\(.channels // 0)"' | sort -t, -k2 -rn | cut -d, -f1 | head -1)

if [ -z "$EAC3" ]; then
  echo "⚠ No English EAC3 audio found (will skip .eac3 extraction)"
  EAC3_FOUND=0
else
  echo "✓ English EAC3 audio: 0:$EAC3"
  EAC3_FOUND=1
fi

# Get ALL English SRT subtitles
SRT_SUBS=$(echo "$STREAMS" | jq -r '.streams[] | select(.codec_type=="subtitle" and .codec_name=="subrip" and (.tags.language=="eng" or .tags.language==null or .tags.language=="")) | .index')

# Fallback: if no SRT, get first English PGS, then VobSub
if [ -z "$SRT_SUBS" ]; then
  echo "  No English SRT subs, trying PGS fallback..."
  FALLBACK=$(echo "$STREAMS" | jq -r '.streams[] | select(.codec_type=="subtitle" and .codec_name=="hdmv_pgs_subtitle" and (.tags.language=="eng" or .tags.language==null or .tags.language=="")) | .index' | head -1)

  if [ -z "$FALLBACK" ]; then
    echo "  No English PGS subs, trying VobSub fallback..."
    FALLBACK=$(echo "$STREAMS" | jq -r '.streams[] | select(.codec_type=="subtitle" and .codec_name=="dvdsub" and (.tags.language=="eng" or .tags.language==null or .tags.language=="")) | .index' | head -1)
  fi

  if [ -n "$FALLBACK" ]; then
    SRT_SUBS="$FALLBACK"
    echo "✓ Using fallback subtitle: 0:$FALLBACK"
  else
    echo "⚠ No English subtitles found (SRT, PGS, or VobSub)"
  fi
else
  echo "✓ English subtitles: $(echo $SRT_SUBS | tr '\n' ' ')"
fi

# Build ffmpeg map arguments
MAP_ARGS="-map 0:$VIDEO -map 0:$TRUEHD"

# Add all subtitle tracks
for sub in $SRT_SUBS; do
  MAP_ARGS="$MAP_ARGS -map 0:$sub"
done

echo ""
echo "Extracting streams..."

# Run ffmpeg - one shot, two outputs (or just one if no EAC3)
if [ $EAC3_FOUND -eq 1 ]; then
  ffmpeg -i "$INPUT" \
    $MAP_ARGS \
    -c copy \
    "$OUTPUT_MKV" \
    -map "0:$EAC3" \
    -c:a copy \
    "$OUTPUT_EAC3"

  echo ""
  echo "✓ Created: $OUTPUT_MKV (video + TrueHD + subs)"
  echo "✓ Created: $OUTPUT_EAC3 (English EAC3)"
else
  ffmpeg -i "$INPUT" \
    $MAP_ARGS \
    -c copy \
    "$OUTPUT_MKV"

  echo ""
  echo "✓ Created: $OUTPUT_MKV (video + TrueHD + subs)"
fi
