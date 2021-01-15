# blog hugo

fetch issues from github (using [github-issue-fetcher](https://github.com/jrdeng/github-issue-fetcher)),

and generate static website (using [hugo](https://gohugo.io/)).


## Usage

1. create your github page repo
2. clone this repo (with all submodules)
3. modify `config.toml` and themes as you want
4. run `generate_and_deploy.py`


```
$ ./generate_and_deploy.py OPTIONS
OPTIONS:
        -t|--token      github token for GraphQL
        -o|--owner      repo owner(login)
        -r|--repo       repo name(without .git suffix) to fetch issue and push the site
        -g|--gen        path to the blog generator(hugo)
        -l|--local      generate and deploy site without pulling new issues(useing local MD, -t will be ignored)
        -d|--dry        dry run, just generate site, but do not deploy it
```


