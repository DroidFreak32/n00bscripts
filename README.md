# n00bscripts
## Replace text from files
```bash
perl -pi -w -e 's/<OLD>/<NEW>/g;' <filename>
```
Replace `<OLD>` with the current tag and `<NEW>` with the new one

## Recursively Check for missing/corrupted FLAC files
```bash
grep -a -L -r -E --include="*.flac" "libFLAC|fLaC"
```
## Check for files that weren't properly encoded to OPUS
```bash
# Finds all *.flac files and sends the sorted list to a.txt
find . -name "*.flac" | sort > a.txt

# Using git to commit the file list inorder to do a git diff later. 
git init . ; git add a.txt ; git commit -m "Init"

# Finds all encoded *.opus files, renames the extension to .flac and overwrites a.txt with the new list.
find . -name "*.opus" | sort | sed 's/.opus$/.flac/g;' > a.txt

# The FLAC files which are corrupted are now shown "missing" in the new list (As they couldn't be encoded).
git diff a.txt
```

## Archive SCANS folders from FLAC rips to reduce no. of files.
```bash
export CWD="$PWD"
export array=()
while IFS=  read -r -d $'\0'; do
    array+=("$REPLY")
done < <(find . -type d \( -iname "scan*" -o -iname "*bookl*" \) -print0)
for i in "${array[@]}"
do
        BASEDIRNAME=$(basename "$i")
        PARENTDIRNAME=$(dirname "$i")
        cd "$PARENTDIRNAME"
        rar a "$BASEDIRNAME".rar -m0 -df "$BASEDIRNAME"
        cd "$CWD"
done
```

## Backup the rootfs of Ubuntu 18.04 with Multi-Threaded compression (Requires pxz).
```bash
XZ_OPT=-9 tar -I pxz -cp \
--exclude=/backup.txz.gpg \
--exclude=/proc \
--exclude=/tmp \
--exclude=/mnt \
--exclude=/dev \
--exclude=/sys \
--exclude=/swap.img \
--exclude=/run \
--exclude=/media \
--exclude=/var/log \
--exclude=/var/cache/apt/archives \
--exclude=/usr/src/linux-headers* \
--exclude=/home/*/.gvfs \
--exclude=/home/*/.cache \
--exclude=/home/*/.ccache \
--exclude=/home/*/.local/share/Trash \
--exclude=/home/*/los \
--exclude=/home/*/.gdfuse/*/cache / | gpg -e -r <email id> -o backup.txz.gpg
```

## To extract the backup and install the system:
```bash
gpg --armor  --export-secret-keys <email id> > private.key
gpg --import private.key
gpg -d backup.txz.gpg | tar -xJ

for i in /dev /dev/pts /proc /sys /run; do sudo mount -B $i /mnt$i; done
chroot /mnt
grub-install /dev/sda
```
