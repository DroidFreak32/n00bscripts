### Add remote to all repos that match my custom group EXTRAS
```bash
repo forall -g EXTRAS -c 'echo git remote add LineageOS git@github.com:$(echo ${REPO_PROJECT} | sed "s|ROM-EXTRAS|LineageOS|g;")'
```
### Check current HEAD of custom repos
```
repo forall -v -g EXTRAS -c "git log --oneline | head -n1"
```
### List of all repos not matching manifest branch
```
repoheads () {
    repo forall -pv -g EXTRAS -c "git log --oneline | head -n1" | grep -v github-ssh/lineage-19.1 | grep HEAD -B1 |grep project | cut -d' ' -f2
}
# Now use a loop to so whatever is needed
for i in $(repoheads); do git rebase -f github-ssh/lineage-19.1 --exec="git commit --amend --no-edit"
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
### Gerrit - Function to give replaced project name
```
repoproj (){
file="${1:-.}"
        repo info $file | grep Project | cut -d" " -f2 | sed 's/ROM-EXTRAS/LineageOS/g'
}
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
### Gerrit: List all changes that have a topic:
```bash
gerrit query 'intopic:^.+'
```
### Gerrit: Undo all merges in project
```bash
# 1) Query all current ref: refs/changes/xx/yy and save it to a temp file
gerrit query --current-patch-set 'project:LineageOS/android_packages_apps_Settings status:merged' | egrep "^    ref:" | cut -d' ' -f6 >/tmp/CHANGES_NUMBERS

# Example output
# $ head /tmp/CHANGES_NUMBERS
# refs/changes/23/1823/1
# refs/changes/39/39/2
# refs/changes/44/144/2

# 2) Replace the last digit in the ref with "meta"
for i in `cat /tmp/CHANGES_NUMBERS`; do echo "$(dirname $i)/meta"; done > /tmp/CHANGES_NUMBERS2

# Example output
# $ head /tmp/CHANGES_NUMBERS2
# refs/changes/23/1823/meta
# refs/changes/39/39/meta
# refs/changes/44/144/meta

# 3) Copy /tmp/CHANGES_NUMBERS2 to the gerrit server
# 4) IMPORTANT!! Stop the gerrit instance and cd into the project's .git directory
#    Make sure git log refs/changes/xx/yy/meta returns a log!
# 5) Backup the `packed-refs` file somewhere safe
# 6) Replace all matching refs' commit hash from /tmp/CHANGES_NUMBERS2 with refs/changes/xx/yy/meta~1

for i in `cat /tmp/CHANGES_NUMBERS2`
do
    CURRENT="$(git rev-parse $i)";
    REPLACE="$(git rev-parse $i~1)";
    sed -i "s|$CURRENT $i|$REPLACE $i|g;" ~/packed-refs
done
```
