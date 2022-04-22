### Add remote to all repos that match my custom group EXTRAS
```bash
repo forall -g EXTRAS -c 'echo git remote add LineageOS git@github.com:$(echo ${REPO_PROJECT} | sed "s|ROM-EXTRAS|LineageOS|g;")'
```
