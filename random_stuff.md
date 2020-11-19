## There are just few simple shell I keep forgetting. Hopefully I don't get lazy to update this file after I google the things I need.

#### `find` and empty the contents of files:

```bash
find . -type f -exec truncate -s 0 {} \;
```
---
#### Take each line from a text file as an input (useful if you redirect the o/p of a find result to a file.
 - #### *This MAY NOT escape special characters!*
```bash
while read p; do ls -al "$p" ; done < list.txt
```
---
#### [Build AOSP without getting bullied by metalava](https://sx.ix5.org/info/building-android/#fnref:2)
```bash
WITHOUT_CHECK_API=true
```
---
#### [Screen - start screen in detached mode](https://superuser.com/a/454914)
```bash
screen -d -m <yourcommand>
```
---