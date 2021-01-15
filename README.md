# blog hugo

fetch issues from github (using [github-issue-fetcher](https://github.com/jrdeng/github-issue-fetcher)),

and generate static website (using [hugo](https://gohugo.io/)).


## Features

- write blog anywhere - just open the github issue in a browser. (open, free, geek...)
- comments of blog posts are also in the issues (using [utterances](https://utteranc.es/))
- powered by [hugo](https://gohugo.io/)

take [my blog](https://github.com/jrdeng/jrdeng.github.io) as a sample.


## Usage

1. create your github page repo
2. get a `token` to access the GraphQL API to fetch the issues, please take a look at [Authenticating with GraphQL](https://developer.github.com/v4/guides/forming-calls/#authenticating-with-graphql)
3. clone this repo (with all submodules), and install dependent Python3 modules and hugo
4. modify `config.toml` and themes as you want
5. run `generate_and_deploy.py`


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


