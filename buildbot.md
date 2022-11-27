### Add remote to all repos that match my custom group EXTRAS
```bash
repo forall -g EXTRAS -c 'echo git remote add LineageOS git@github.com:$(echo ${REPO_PROJECT} | sed "s|ROM-EXTRAS|LineageOS|g;")'
```
### Check current HEAD of custom repos
```
repo forall -v -g EXTRAS -c "git log --oneline | head -n1"
```
### Generate custom repos `project-list` array to use with `repo start/upload`
```
A=($(repo forall -g EXTRAS -c "echo \$REPO_PATH"))
repo start lineage-19.1 "${A[@]}"
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
```bash
#gerrit is aliased to 'ssh -p <port> user@gerrithost gerrit'
gerrit query --current-patch-set  'status:abandoned' | egrep '^    revision' | awk '{print $2}' > CHANGES_NUMBERS
for i in `cat CHANGES_NUMBERS`; do gerrit review --restore $i; done
 ```
### Repo - Get PWD's REPO_PROJECT for gerrit
```bash
repo info . | grep Project | cut -d" " -f2
```
### Gerrit: force create project and update branch baseline
```
gerrit create-project LineageOS/android_packages_modules_Connectivity
git push lgerrit:`repoproj` HEAD:refs/heads/master -o skip-validation
gerrit create-branch `repoproj` lineage-19.1 ded73434a
```
