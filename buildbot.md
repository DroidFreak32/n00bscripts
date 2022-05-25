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
