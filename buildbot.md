### Add remote to all repos that match my custom group EXTRAS
```bash
repo forall -g EXTRAS -c 'echo git remote add LineageOS git@github.com:$(echo ${REPO_PROJECT} | sed "s|ROM-EXTRAS|LineageOS|g;")'
```
### Check current HEAD of custom repos
```bash
repo forall -v -g EXTRAS -c "git log --oneline | head -n1"
```
### List of all repos not matching manifest branch
```bash
repoheads () {
    repo forall -pv -g EXTRAS -c "git log --oneline --decorate | head -n1" | grep -v github-ssh/lineage-19.1 | grep HEAD -B1 |grep project | cut -d' ' -f2
}
# Now use a loop to so whatever is needed
for i in $(repoheads); do git rebase -f github-ssh/lineage-19.1 --exec="git commit --amend --no-edit"
```
### Generate custom repos `project-list` array to use with `repo start/upload`
```bash
A=($(repo forall -g EXTRAS -c "echo \$REPO_PATH"))
repo start lineage-19.1 "${A[@]}"
```

### Save list of extras repos to use it in a loop
```bash
extras(){
    repo forall -v -g EXTRAS -c 'echo $REPO_PATH'
}
```
### compare missing commits between repos

```bash
git log --oneline  github/lineage-19.1..HEAD | awk '{first = $1; $1 = ""; print $0, "#", first; }'
git log --oneline  github/lineage-19.1..<diffrepo> | awk '{first = $1; $1 = ""; print $0, "#", first; }'
# Remove known misses, sort both, send to diffchecker
```
### Gerrit - Function to give replaced project name
```bash
repoproj (){
file="${1:-.}"
        repo info $file | grep Project | cut -d" " -f2 | sed 's/ROM-EXTRAS/LineageOS/g'
}
```
Alternative, needs [patches](https://github.com/OSS-App-Forks/git-repo) in the repo tool
```bash
repoproj (){
        file="${1:-.}"
        repo info $file | grep 'ReviewProject' | cut -d" " -f2
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
```bash
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
### Sanitizing gerrit's json.
In this example I will be creating a mapping ChangeID <-> Topic

1) Get all changes that have a topic and are merged:
```bash
gerrit query --current-patch-set 'intopic:^.+ status:merged' --no-limit --format=JSON > topics.json
```
2) Sanitize the json by [filtering all the unnecessary details](https://stackoverflow.com/a/46293052/6437140), and avoiding [empty lines](https://stackoverflow.com/a/26196653/6437140):
```bash
cat topics.json | jq 'with_entries(select([.key] | inside(["id", "topic"])))' | jq -c 'select(length > 0)' > gerrit.json
```
This gives us a file that looks like:
```json
{"topic":"ui-ux-improvements","id":"I1eb602412b25fc0741a75a5fd31ddcbe23fd8885"}
{"topic":"screenshot-improvements","id":"I03b2db8a16078a91db12ddc1c3346d4a8ff0895c"}
{"topic":"screenshot-improvements","id":"I361c7ae4bf74f2dd67b86e960f8d2d6ef63f5b8f"}
{"topic":"screenshot-improvements","id":"If413241c3fa533650690cf3b7df5c05fb2f8c8ed"}
{"topic":"screenshot-improvements","id":"I7669769ca3104b3566ed38f549af384f83d92d81"}
{"topic":"screenshot-improvements","id":"Ic8318cdb72a64da8eeb7d0966d45314d450d2d39"}
```

### Undo-ing gerrit merge
Refer my comment [here](https://stackoverflow.com/a/76076081/6437140)  
This script is called via SSH to the gerrit server's HOST (Not the gerrit's SSH!)  
Example of execution with script saved in my Gerrit Host's ~/gerrit/scripts/undo_merge.sh
```bash
ssh root@gerrithost 'GERRIT_REPO="LineageOS/android_vendor_lineage" ~/gerrit/scripts/undo_merge.sh'
```
Script: [LINK](dumps/undo_merge.sh)

### Picks
```bash
384033
384034
384498
384499
```
