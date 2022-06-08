# n00bscripts & configs

## WireGuard config to "split-tunnel" into a VPN,

Within your VPN-provider's WireGuard config you need to make a couple of changes Inside `[Interface]` Section.  
I named it wg-vpn.conf

```ini
[Interface]
# Prevent WireGuard from creating any routing tables.
# You definitely don't want your existing PiHole users to go get access to this VPN
Table = off

# Create a new Routing table specific to clients connecting to VPN
PostUp = ip route add default dev wg-vpn table 1337
PreDown = ip route del default dev wg-vpn table 1337
```

Then you need to create a new WireGuard "bridge" interface config.  
This cannot be your DNS-only/PiHole interface because it would then depend on `wg-vpn` interface to be always up.

I have set up my bridge interface like so:

```ini
[Interface]
Address = <NEW SUBNET (10.10.0.1/24)>
ListenPort = <PORT>
PrivateKey = <NEW PRIVATE KEY>
Table = off

# Start the VPN interface
PreUp = wg-quick up wg-vpn
# Use the VPN interface for all traffic
PostUp = iptables -w -t nat -A POSTROUTING -o wg-vpn -j MASQUERADE ; ip6tables -w -t nat -A POSTROUTING -o wg-vpn -j MASQUERADE

# All packets from this "bridge" should use our custom routing table using the VPN
PostUp = ip rule add from 10.10.0.0/24 lookup 1337
# Make this subnet reachable through this interface for all incoming packets from VPN
PostUp = ip route add 10.10.0.0/24 dev %i table 1337

# Cleanup
PreDown = ip rule del from 10.10.0.0/24 lookup 1337
PostDown = iptables -w -t nat -D POSTROUTING -o wg-vpn -j MASQUERADE; ip6tables -w -t nat -D POSTROUTING -o wg-vpn -j MASQUERADE
PostDown = wg-quick down wg-vpn

# oneplus8t-rushab
[Peer]
PublicKey = <PUB>
PresharedKey = <PSK>
AllowedIPs = 10.10.0.2/32
```
TODO:
- Figure out why the main routing table contains bridge0 route despite Table = off
- Implement Firewall to block anything outside this network
- Figure out fwmask

---

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
# This may be useful: https://github.com/azuer88/grub-mkconfig_lib-patch
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

## Modify Media file timestamps from the names
#### Must be of format IMG-YYYYMMDD-randomtext.jpg"
```bash
for i in "$(cat /sdcard/WAIMAGES.txt)"
do
    TIMESTAMP="$(echo $i | awk -F '-' '{print $2}')";
    touch -c -t "$TIMESTAMP" $i
    ls -l $i
done
```
####  This is for format IMG_20190629_142823_662.jpg used by telegram
```bash
find . -type f -name "*201*" > /sdcard/tg.txt
for i in "$(cat /sdcard/tg.txt)"
do
    TIMESTAMP="$(echo $i | awk -F '_' '{print $2$3$4}')";
    TIMESTAMP="${TIMESTAMP::-4}" # Remove extension
    touch -c -t "${TIMESTAMP:0:12}.${TIMESTAMP:12}" $i
    ls -l $i
done
```


## ADB - recursively scan media from file list
```bash
for i in $(cat /sdcard/WAIMAGES.txt)
do
    am broadcast -a "android.intent.action.MEDIA_SCANNER_SCAN_FILE" -d file://"$PWD/$i" ;
done
```

## RSync - Sync sdcard & PC, remove deleted items in target
 - Phone to PC
```bash
rsync -av --recursive -P --dry-run -e "ssh -i /data/ssh/ssh_host_rsa_key" /sdcard/ username@IP:~/Android/sdcard --delete
```
 - PC to Phone (Needs root for `/sdcard/Android/obb` )
```bash
rsync -av --recursive -P --dry-run -e  "ssh -i /sdcard/.ssh/id_ed25519" username@IP:~/Android/sdcard/ /sdcard --delete
```


## There are just few simple shell 1-liners I keep forgetting. Hopefully I don't get lazy to update this file after I google the things I need.

#### `find` and empty the contents of files:

```bash
find . -type f -exec truncate -s 0 {} \;
```
---
#### Take each line from a text file as an input (useful if you redirect the o/p of a find result to a file).
 - #### *This MAY NOT escape special characters!*
```bash
while read p; do ls -al "$p" ; done < list.txt
```
---
#### [Build AOSP without getting bullied by metalava](https://sx.ix5.org/info/building-android/#fnref:2)
 - ##### *NOTE: Does not seem to work :(*
```bash
WITHOUT_CHECK_API=true
```
---
#### [Screen - start screen in detached mode](https://superuser.com/a/454914)
```bash
screen -d -m <yourcommand>
```
---
#### Gerrit - search term to view all merged non-device related changes
```
status:merged -project:^LineageOS/android_device.+  -project:^LineageOS/android_kernel.+
```
---
#### RAR Archive folders with password in background:
```bash
for i in *NEF; do screen -d -m rar a -p'password' ~/Pictures/"$i.rar" -m0 -v500M -r "$i"/* ; done
```
---
#### [`find` multiple matching names using OR operation and exec a command](https://unix.stackexchange.com/a/50613)
```bash
find . -type f \( -name "*REAL*" -o -name "*FAKE*" -o -name "*mp3" \) -exec basename {} \;
```
---
#### `find` above and create replica dir structure from the result
 - ##### *Not tested against specal characters*
```bash
 find . -type f \( -name "*REAL*" -o -name "*FAKE*" -o -name "*mp3" \) -exec dirname {} \; | xargs -I {} bash -c 'mkdir -p ./FAKES/"{}"'
```
---
#### [`find` Directory structure as CSV](https://stackoverflow.com/a/58606757)
```bash
find . -maxdepth 2 -mindepth 2 -type d | sort | sed 's:./::;s:/:",":;s:^:":;s:$:":g;' > file.csv
```
---
#### [`sed` - Convert synced LRC to unsynced LRC](https://unix.stackexchange.com/a/187894/261206)
```bash
sed -r -i 's/^\[(.*)\]//' "$FILE"
```
---
#### [RegEx to match duplicate lines](https://stackoverflow.com/questions/1573361)
```bash
^(.*)(\r?\n\1)+$
```

#### Substitute find result as argument in a command and run it in background
```bash
find -iname "*flac" -exec ls -Q {} \; | sed 's/$/ \&/; s/^/md5sum /' > ~/tmp/bg_tasks.sh
```

#### [And then run 10 threads, wait for it to finish, run 10 more.](https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0)
```bash
 sed '0~10 s/$/\nwait\necho WAITING.../' < bg_tasks.sh > waiting_tasks.sh
```
---
#### [Find & display only files that do not have lyrics](https://stackoverflow.com/questions/23740545/how-to-print-only-the-unique-lines-in-bash)
```bash
find \( -name "*lrc" -o -name "*flac" \) | sed -e "s/.flac$//g;" -e "s/.lrc$//g;" | sort | uniq -u
```
---

#### [AWK - Netstat - Print time and connections](https://stackoverflow.com/questions/17001849/awk-partly-string-match-if-column-word-partly-matches)
```bash
awk -F '[[:space:]][[:space:]]+' ' $1~/TIMEST/ { print } { print $5 }' /tmp/netstat_connections.txt | head
```
---

#### [Regex match all language characters, but stop at 2nd occurrance of tab](https://stackoverflow.com/questions/2013124/regex-matching-up-to-the-first-occurrence-of-a-character)
```perl
^(ID|[0-9]+)\t+([\x00-\x7F]|[^\x00-\x7F])(.*?)\t

Example:
ID			artist	title	error
91092377	Seether	I've Got You Under My Skin	Your account can't stream the track from your current country and no alternative found.

Matches till BEFORE the TITLE column 
```
---

#### NX Tar extract manually collected bundles and strip unnecesarry folders:
```bash
for i in *tar.gz; do j="${i%.tar.gz}"; mkdir $j; tar -C $j -xf $i --strip-components=4; done
```
---

#### [Print all lines after matched pattern](https://stackoverflow.com/questions/5346896/print-everything-on-line-after-match)
```bash
awk '/### begin/ {seen = 1} seen {print}' wg0.conf
```
---
#### [AWK - Print first column after all other columns](https://stackoverflow.com/a/4198169/6437140)
```bash
$ git log --oneline COMMIT~1..COMMIT | awk '{first = $1; $1 = ""; print $0, first; }'
 <COMMITmessage> <commitsha>
```
