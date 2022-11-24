### Add remote to all repos that match my custom group EXTRAS
```bash
repo forall -g EXTRAS -c 'echo git remote add LineageOS git@github.com:$(echo ${REPO_PROJECT} | sed "s|ROM-EXTRAS|LineageOS|g;")'
```
### compare missing commits between repos

```bash
git log --oneline  github/lineage-19.1..HEAD | awk '{first = $1; $1 = ""; print $0, "#", first; }'
git log --oneline  github/lineage-19.1..<diffrepo> | awk '{first = $1; $1 = ""; print $0, "#", first; }'
# Remove known misses, sort both, send to diffchecker
```
### Find changeIDs that are duplicates
```bash
git log <commit>..HEAD | grep Change-Id | awk '{print $2}' | sort | uniq -d
```
### Gerrit - Batch restore all abandoned commits
```
#gerrit is aliased to 'ssh -p <port> user@gerrithost gerrit'
gerrit query --current-patch-set  'status:abandoned' | egrep '^    revision' | awk '{print $2}' > CHANGES_NUMBERS
for i in `cat CHANGES_NUMBERS`; do gerrit review --restore $i; done
 ```
