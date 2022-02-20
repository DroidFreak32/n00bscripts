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
### [`find` Directory structure as CSV](https://stackoverflow.com/a/58606757)
```bash
find . -maxdepth 2 -mindepth 2 -type d | sort | sed 's:./::;s:/:",":;s:^:":;s:$:":g;' > file.csv
```
---
### [`sed` - Convert synced LRC to unsynced LRC](https://unix.stackexchange.com/a/187894/261206)
```bash
sed -r -i 's/^\[(.*)\]//' "$FILE"
```
---
### [RegEx to match duplicate lines](https://stackoverflow.com/questions/1573361)
```bash
^(.*)(\r?\n\1)+$
```

### Substitute find result as argument in a command and run it in background
```bash
find -iname "*flac" -exec ls -Q {} \; | sed 's/$/ \&/; s/^/md5sum /' > ~/tmp/bg_tasks.sh
```

### [And then run 10 threads, wait for it to finish, run 10 more.](https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0)
```bash
 sed '0~10 s/$/\nwait\necho WAITING.../' < bg_tasks.sh > waiting_tasks.sh
```
---
### [Find & display only files that do not have lyrics](https://stackoverflow.com/questions/23740545/how-to-print-only-the-unique-lines-in-bash)
```
for i in $(find \( -name "*lrc" -o -name "*flac" \) -exec basename {} \; ); do echo "${i%.*}" ; done | sort | uniq -u
```
---

### [AWK - Netstat - Print time and connections](https://stackoverflow.com/questions/17001849/awk-partly-string-match-if-column-word-partly-matches)
```bash
awk -F '[[:space:]][[:space:]]+' ' $1~/TIMEST/ { print } { print $5 }' /tmp/netstat_connections.txt | head
```
### [Regex match all language characters, but stop at 2nd occurrance of tab](https://stackoverflow.com/questions/2013124/regex-matching-up-to-the-first-occurrence-of-a-character)
```perl
^(ID|[0-9]+)\t+([\x00-\x7F]|[^\x00-\x7F])(.*?)\t

Example:
ID			artist	title	error
91092377	Seether	I've Got You Under My Skin	Your account can't stream the track from your current country and no alternative found.

Matches till BEFORE the TITLE column 
```
