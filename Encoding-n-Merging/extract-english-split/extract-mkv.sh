#!/bin/bash
set -e

INPUT=""
OUTPUT_MKV=""
OUTPUT_EAC3=""
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
      elif [ -z "$OUTPUT_MKV" ]; then
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

# If output names not specified, derive from input filename
if [ -z "$OUTPUT_MKV" ]; then
  BASENAME=$(basename "$INPUT" .mkv)
  OUTPUT_MKV="${BASENAME}.mkv"
  OUTPUT_EAC3="${BASENAME}.en"
elif [ -z "$OUTPUT_EAC3" ]; then
  BASENAME=$(basename "$OUTPUT_MKV" .mkv)
  OUTPUT_EAC3="${BASENAME}.en"
fi

# Create output directory if specified
if [ -n "$OUTPUT_DIR" ]; then
  mkdir -p "$OUTPUT_DIR"
  OUTPUT_MKV="$OUTPUT_DIR/$OUTPUT_MKV"
  OUTPUT_EAC3="$OUTPUT_DIR/$OUTPUT_EAC3"
else
  # If no output dir specified, get input directory
  INPUT_DIR=$(dirname "$INPUT")
  if [ "$INPUT_DIR" = "." ]; then
    INPUT_DIR=""
  else
    INPUT_DIR="${INPUT_DIR}/"
  fi
fi

# Check if input and output would be the same (same directory and basename)
INPUT_BASENAME=$(basename "$INPUT")
OUTPUT_MKV_BASENAME=$(basename "$OUTPUT_MKV")

if [ "$INPUT_BASENAME" = "$OUTPUT_MKV_BASENAME" ]; then
  # Prefix with rip- to avoid overwriting
  OUTPUT_MKV_BASENAME="rip-${OUTPUT_MKV_BASENAME}"
  OUTPUT_EAC3_BASE=$(basename "$OUTPUT_EAC3")
  OUTPUT_EAC3_BASENAME="rip-${OUTPUT_EAC3_BASE}"

  if [ -n "$OUTPUT_DIR" ]; then
    OUTPUT_MKV="$OUTPUT_DIR/$OUTPUT_MKV_BASENAME"
    OUTPUT_EAC3="$OUTPUT_DIR/$OUTPUT_EAC3_BASENAME"
  else
    OUTPUT_MKV="${INPUT_DIR}${OUTPUT_MKV_BASENAME}"
    OUTPUT_EAC3="${INPUT_DIR}${OUTPUT_EAC3_BASENAME}"
  fi
fi

# Append codec extension to fallback audio
if [ $FALLBACK_FOUND -eq 1 ]; then
  OUTPUT_EAC3="${OUTPUT_EAC3}.${FALLBACK_CODEC}"
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

# Get master audio (priority: TrueHD > DTS-HD > DTS)
MASTER=""
for codec in "truehd" "dtshd" "dts"; do
  MASTER=$(echo "$STREAMS" | jq -r ".streams[] | select(.codec_type==\"audio\" and .codec_name==\"$codec\" and (.tags.language==\"eng\" or .tags.language==null or .tags.language==\"\")) | .index" | head -1)
  if [ -n "$MASTER" ]; then
    CODEC_NAME=$(echo "$codec" | tr '[:lower:]' '[:upper:]')
    echo "✓ Master audio ($CODEC_NAME): 0:$MASTER"
    break
  fi
done

if [ -z "$MASTER" ]; then
  echo "Error: No English master audio found (TrueHD, DTS-HD, or DTS)"
  exit 1
fi

# Get fallback audio (priority: EAC3 > AC3 > AAC), pick the one with most channels if multiple exist
FALLBACK=""
FALLBACK_CODEC=""
for codec in "eac3" "ac3" "aac"; do
  FALLBACK=$(echo "$STREAMS" | jq -r ".streams[] | select(.codec_type==\"audio\" and .codec_name==\"$codec\" and (.tags.language==\"eng\" or .tags.language==null or .tags.language==\"\") and .index != $MASTER) | \"\(.index),\(.channels // 0)\"" | sort -t, -k2 -rn | cut -d, -f1 | head -1)
  if [ -n "$FALLBACK" ]; then
    CODEC_NAME=$(echo "$codec" | tr '[:lower:]' '[:upper:]')
    echo "✓ Fallback audio ($CODEC_NAME): 0:$FALLBACK"
    FALLBACK_CODEC="$codec"
    FALLBACK_FOUND=1
    break
  fi
done

if [ -z "$FALLBACK" ]; then
  echo "⚠ No English fallback audio found (EAC3, AC3, or AAC) (will skip fallback extraction)"
  FALLBACK_FOUND=0
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

# Run ffmpeg - one shot, two outputs (or just one if no fallback)
if [ $FALLBACK_FOUND -eq 1 ]; then
  ffmpeg -i "$INPUT" \
    $MAP_ARGS \
    -c copy \
    "$OUTPUT_MKV" \
    -map "0:$FALLBACK" \
    -c:a copy \
    "$OUTPUT_EAC3"

  echo ""
  echo "✓ Created: $OUTPUT_MKV (video + master audio + subs)"
  echo "✓ Created: $OUTPUT_EAC3 (English fallback audio)"
else
  ffmpeg -i "$INPUT" \
    $MAP_ARGS \
    -c copy \
    "$OUTPUT_MKV"

  echo ""
  echo "✓ Created: $OUTPUT_MKV (video + master audio + subs)"
fi
