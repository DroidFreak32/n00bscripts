```bash
find . -type f -iname "*.jpg" -o -iname "*.mp4" -o -iname "*.NEF" -o -iname "*.MOV" -o -iname "*.JPG"
find . -type f | grep -vE ".jpg|.mp4|.NEF|.MOV|.JPG|.MP4"

grep -vE ".jpg|.mp4|.NEF|.MOV|.JPG"

find . -type f \( -iname "*.jpg" -o -iname "*.mp4" -o -iname "*.NEF" -o -iname "*.MOV" -o -iname "*.JPG" -o -iname "*.MP4" \)

#for f in *.png *.jpg *.jpeg *.dng *.NEF *.HEIC; do
for f in *; do
    EPOCH="$(exiftool -s3 -datetimeoriginal -d "%s" "$f")";
    EPOCH_MS="$(exiftool -s3 -SubsecTimeOriginal -d "%s" "$f" | sed 's/ //g;')";
    MODTIME=$(date -d@$EPOCH.$EPOCH_MS "+%Y-%m-%dT%H:%M:%S.%3N")
    echo "$f --> $MODTIME";
    touch -c --date="@$EPOCH" "$f"
    touch -c --date="@$EPOCH.$EPOCH_MS" "$f"
    echo "====";
done

for i in *.MP4;
do
    TIMESTAMP="$(echo ${i:4:18} | sed 's/_//g;')";
    MODTIME="${TIMESTAMP:0:4}-${TIMESTAMP:4:2}-${TIMESTAMP:6:2}T${TIMESTAMP:8:2}:${TIMESTAMP:10:2}:${TIMESTAMP:12:2}.${TIMESTAMP:14:3}"
    echo "$i --> $MODTIME";
    echo touch -c -d "$MODTIME" "$i"
    echo "====";
done


# no MS
for i in *.3gp;
do
    TIMESTAMP="$(echo ${i:4:18} | sed 's/_//g;')";
    MODTIME="${TIMESTAMP:0:4}-${TIMESTAMP:4:2}-${TIMESTAMP:6:2}T${TIMESTAMP:8:2}:${TIMESTAMP:10:2}:${TIMESTAMP:12:2}"
    echo "$i --> $MODTIME";
    touch -c -d "$MODTIME" "$i"
    echo "====";
done

# Samsung no MS 20170730_111252.mp4
for i in *;
do
    TIMESTAMP="$(echo ${i:0:15} | sed 's/_//g;')";
    MODTIME="${TIMESTAMP:0:4}-${TIMESTAMP:4:2}-${TIMESTAMP:6:2}T${TIMESTAMP:8:2}:${TIMESTAMP:10:2}:${TIMESTAMP:12:2}"
    echo "$i --> $MODTIME";
    echo touch -c -d "$MODTIME" "$i"
    echo "====";
done


# For PXL_ and offset date

add() { n="$@"; bc <<< "${n// /+}"; }
for i in PXL_2025*.mp4;
do
    TIMESTAMP="$(echo ${i:4:18} | sed 's/_//g;')";
    MODTIME="${TIMESTAMP:0:4}-${TIMESTAMP:4:2}-${TIMESTAMP:6:2}T${TIMESTAMP:8:2}:${TIMESTAMP:10:2}:${TIMESTAMP:12:2}.${TIMESTAMP:14:3}"
    EPOCH_OLD=$(date +"%s.%3N" -d $MODTIME)
    EPOCH=$(add $EPOCH_OLD 19800.000)
    #EPOCH=$(add $EPOCH_OLD 0.0)
    echo "$i --> $(date -d@$EPOCH)"
    echo touch -c --date="@$EPOCH" "$i"
    echo "====";
done

# Oneplus VIDYYYYDDMMhhmmss.mp4

for i in VID*.mp4;
do
    TIMESTAMP="${i:3:14}";
    MODTIME="${TIMESTAMP:0:4}-${TIMESTAMP:4:2}-${TIMESTAMP:6:2}T${TIMESTAMP:8:2}:${TIMESTAMP:10:2}:${TIMESTAMP:12:2}"
    EPOCH_OLD=$(date +"%s.%3N" -d $MODTIME)
    #EPOCH=$(add $EPOCH_OLD 19800.000)
    EPOCH=$(add $EPOCH_OLD 0.0)
    echo "$i --> $(date -d@$EPOCH)"
    touch -c --date="@$EPOCH" "$i"
    echo "====";
done

# For PXL_ and offset date using Exif
add() { n="$@"; bc <<< "${n// /+}"; }
for i in *.mp4;
do
    TIMESTAMP="$(echo ${i:4:18} | sed 's/_//g;')";
    TIMESTAMP_NS=${TIMESTAMP:14:3}
    EPOCH_OLD="$(exiftool -api largefilesupport=1 -s3 -createdate -d "%s" "$i")";
    EPOCH=$(add $EPOCH_OLD 19800.$TIMESTAMP_NS)
    echo "$i --> $(date -d@$EPOCH)"
    #touch -c --date="@$EPOCH" "$i"
    echo "====";
done

# Other + offset date
for f in *.MP4; do
    EPOCH="$(exiftool -api largefilesupport=1 -s3 -createdate -d "%s" "$f")";
    EPOCH_MS=000
    MODTIME=$(date -d@$EPOCH.$EPOCH_MS "+%Y-%m-%dT%H:%M:%S.%3N")
    echo "$f --> $MODTIME";
    echo touch --date="@$EPOCH.$EPOCH_MS" "$f"
    echo "====";
done


# P7 only
for f in *.MOV; do
    EPOCH_OLD="$(exiftool -api largefilesupport=1 -s3 -createdate -d "%s" "$f")";
    EPOCH=$(($EPOCH_OLD + 19800))
    EPOCH_MS=000
    MODTIME=$(date -d@$EPOCH.$EPOCH_MS "+%Y-%m-%dT%H:%M:%S.%3N")
    echo "$f --> $MODTIME";
    touch -c --date="@$EPOCH.$EPOCH_MS" "$f"
    echo "====";
done

# Pxl only
for f in *.mp4; do
    EPOCH="$(exiftool -api largefilesupport=1 -s3 -createdate -d "%s" "$f")";
    EPOCH_NEW=$(($EPOCH + 19800))
    date -d@$EPOCH
    date -d@$EPOCH_NEW
    echo ===
done


add() { n="$@"; bc <<< "${n// /+}"; }
for i in *.jpg;
do
    TIMESTAMP="$(echo ${i:4:18} | sed 's/_//g;')";
    MODTIME="${TIMESTAMP:14:3}"
    exiftool -o DATECORRECTED/"$i" -s3 -SubsecTimeOriginal=$MODTIME -d "%s" "$i"
    echo ===
done


GPSDateTime                     : 2024:11:23 05:24:30Z
~/.../dcim/Rafting $ exiftool -s -time:all ../Camera/PXL_20250410_125622322.jpg
FileModifyDate                  : 2025:04:10 18:26:25+05:30
FileAccessDate                  : 2025:04:10 18:26:22+05:30
FileInodeChangeDate             : 2025:04:10 18:26:25+05:30
ModifyDate                      : 2025:04:10 18:26:22
DateTimeOriginal                : 2025:04:10 18:26:22
CreateDate                      : 2025:04:10 18:26:22
OffsetTime                      : +05:30
OffsetTimeOriginal              : +05:30
OffsetTimeDigitized             : +05:30
SubSecTime                      : 322
SubSecTimeOriginal              : 322
SubSecTimeDigitized             : 322
ProfileDateTime                 : 2023:03:09 10:57:00
SubSecCreateDate                : 2025:04:10 18:26:22.322+05:30
SubSecDateTimeOriginal          : 2025:04:10 18:26:22.322+05:30
SubSecModifyDate                : 2025:04:10 18:26:22.322+05:30

~/.../dcim/Rafting $ exiftool -s -time:all GOPR9993.JPG
FileModifyDate                  : 2024:11:23 11:29:42+05:30
FileAccessDate                  : 2025:04:10 18:10:55+05:30
FileInodeChangeDate             : 2025:04:10 18:14:20+05:30
ModifyDate                      : 2024:11:23 11:29:42
DateTimeOriginal                : 2024:11:23 11:29:42
CreateDate                      : 2024:11:23 11:29:42
SubSecTime                      : 6990
SubSecTimeOriginal              : 6990
SubSecTimeDigitized             : 6990
GPSTimeStamp                    : 05:24:30
GPSDateStamp                    : 2024:11:23
SubSecCreateDate                : 2024:11:23 11:29:42.6990
SubSecDateTimeOriginal          : 2024:11:23 11:29:42.6990
SubSecModifyDate                : 2024:11:23 11:29:42.6990
GPSDateTime                     : 2024:11:23 05:24:30Z




OffsetTime="+05:30"
OffsetTimeOriginal="+05:30"
OffsetTimeDigitized="+05:30"
for i in *.JPG;
do
    SubSecCreateDate="$(exiftool -s3 -SubSecCreateDate "$i")"
    echo "OLD: SubSecCreateDate = $SubSecCreateDate"
    SubSecCreateDate="$SubSecCreateDate+05:30"
    echo "NEW: SubSecCreateDate = $SubSecCreateDate"
    SubSecDateTimeOriginal="$(exiftool -s3 -SubSecDateTimeOriginal "$i")"
    echo "OLD: SubSecDateTimeOriginal = $SubSecDateTimeOriginal"
    SubSecDateTimeOriginal="$SubSecDateTimeOriginal+05:30"
    echo "NEW: SubSecDateTimeOriginal = $SubSecDateTimeOriginal"
    SubSecModifyDate="$(exiftool -s3 -SubSecModifyDate "$i")"
    echo "OLD: SubSecModifyDate = $SubSecModifyDate"
    SubSecModifyDate="$SubSecModifyDate+05:30"
    echo "NEW: SubSecModifyDate = $SubSecModifyDate"
done

for i in *.HIEC;
do
    SubSecCreateDate="$(exiftool -s3 -SubSecCreateDate "$i")"
    SubSecCreateDate="${SubSecCreateDate::-1}+05:30"

    SubSecDateTimeOriginal="$(exiftool -s3 -SubSecDateTimeOriginal "$i")"
    SubSecDateTimeOriginal="${SubSecDateTimeOriginal::-1}+05:30"
    
    SubSecModifyDate="$(exiftool -s3 -SubSecModifyDate "$i")"
    SubSecModifyDate="${SubSecModifyDate::-1}+05:30"

    exiftool -o DATECORRECTED/"$i" -OffsetTime="+05:30" \
    -OffsetTimeOriginal="+05:30" \
    -OffsetTimeDigitized="+05:30" \
    -SubSecCreateDate="$EXIFTIME" \
    -SubSecDateTimeOriginal="$EXIFTIME" \
    -SubSecModifyDate="$EXIFTIME" \
    "$i"
done



for i in *; do
 TIMESTAMP=$(grep "$i" metadata_wallpaper.json | jq -r .photoTakenTime.timestamp) ; touch -c -d@$TIMESTAMP "$i"
done
 FILE=IMG_20180922_182436-COLLAGE.jpg
 TIMESTAMP=$(grep $FILE metadata-2023.json | jq -r .photoTakenTime.timestamp)
 touch -c -d@$TIMESTAMP $FILE
 FILE=IMG_20210821_143938-COLLAGE.jpg
 TIMESTAMP=$(grep $FILE metadata-2023.json | jq -r .photoTakenTime.timestamp)
 touch -c -d@$TIMESTAMP $FILE
 FILE=IMG_20191006_201146-COLLAGE.jpg
 TIMESTAMP=$(grep $FILE metadata-2023.json | jq -r .photoTakenTime.timestamp)
 touch -c -d@$TIMESTAMP $FILE


for i in *.MOV; do
    EXIFTIME=$(exiftool -api largefilesupport=1 -s3 -createdate -d "%Y-%m-%dT%H:%M:%S.000+05:30" "$i")
    exiftool -o timed/"$i" \
 -ModifyDate="$EXIFTIME" \
 -DateTimeOriginal="$EXIFTIME" \
 -CreateDate="$EXIFTIME" \
 -SubSecTimeOriginal="$EXIFTIME" \
 -SubSecTimeDigitized="$EXIFTIME" \
 -GPSTimeStamp="$EXIFTIME" \
 -GPSDateStamp="$EXIFTIME" \
 -ProfileDateTime="$EXIFTIME" \
 -SubSecCreateDate="$EXIFTIME" \
 -SubSecDateTimeOriginal="$EXIFTIME" \
 -TrackCreateDate="$EXIFTIME" \
 -TrackModifyDate="$EXIFTIME" \
 -MediaCreateDate="$EXIFTIME" \
 -MediaModifyDate="$EXIFTIME" \
 -CreationDate="$EXIFTIME" \
 -GPSDateTime="$EXIFTIME" "$i"; done


for i in *.mp4; do exiftool -o timed/"$i" \
 -ModifyDate="2019-06-12T17:00:00.000+05:30" \
 -DateTimeOriginal="2019-06-12T17:00:00.000+05:30" \
 -CreateDate="2019-06-12T17:00:00.000+05:30" \
 -SubSecTimeOriginal="2019-06-12T17:00:00.000+05:30" \
 -SubSecTimeDigitized="2019-06-12T17:00:00.000+05:30" \
 -GPSTimeStamp="2019-06-12T17:00:00.000+05:30" \
 -GPSDateStamp="2019-06-12T17:00:00.000+05:30" \
 -ProfileDateTime="2019-06-12T17:00:00.000+05:30" \
 -SubSecCreateDate="2019-06-12T17:00:00.000+05:30" \
 -SubSecDateTimeOriginal="2019-06-12T17:00:00.000+05:30" \
 -TrackCreateDate="2019-06-12T17:00:00.000+05:30" \
 -TrackModifyDate="2019-06-12T17:00:00.000+05:30" \
 -MediaCreateDate="2019-06-12T17:00:00.000+05:30" \
 -MediaModifyDate="2019-06-12T17:00:00.000+05:30" \
 -CreationDate="2019-06-12T17:00:00.000+05:30" \
 -GPSDateTime="2019-06-12T17:00:00.000+05:30" "$i"; done


```
