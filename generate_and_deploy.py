#!/usr/bin/env python3

import sys
import os
import getopt
import shutil
import subprocess
import filecmp
from datetime import datetime, timedelta

blog_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append('{}{}github-issue-fetcher'.format(blog_dir, os.sep))
import fetcher


def usage():
    print('usage: {} OPTIONS'.format(sys.argv[0]))
    print('OPTIONS:')
    print('\t-t|--token\tgithub token for GraphQL')
    print('\t-o|--owner\trepo owner(login)')
    print('\t-r|--repo\trepo name to fetch issue')


def normalize_issue_title(title):
    r = title.replace('/', '_').strip('., ')
    return r


def datetime_to_beijing(iso_str):
    dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
    return (dt + timedelta(hours=8)).isoformat()


def write_hugo_header(md, issue):
    md.write('---\n')
    md.write('title: "{}"\n'.format(issue.title))
    md.write('date: {}+08:00\n'.format(datetime_to_beijing(issue.createdAt)))
    md.write('slug: "{}"\n'.format(issue.id))
    if len(issue.labels) > 0:
        md.write('tags: [\n') # tags begin
        for label in issue.labels:
            md.write('    "{}",\n'.format(label.name))
        md.write(']\n') # tags end
    md.write('---\n\n')


def write_hugo_body(md, issue):
    md.write('{}\n\n'.format(issue.body))
    md.write('---\n\n')
    md.write('## 评论 （移步到 [github]({}) 上留言）\n\n'.format(issue.url))

    # write comments in MD
    for comment in issue.comments:
        md.write('---\n\n')
        md.write('<img src="{}" alt="{}" width="20" height="20"/> <b>{} 发表于 {}</b>\n\n'.format(comment.author.avatarUrl, comment.author.login, comment.author.login, datetime_to_beijing(comment.createdAt).replace('T', ' ')))
        md.write('{}\n\n'.format(comment.body))


def generate_md(issue_list, output_dir):
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir, True)
    os.mkdir(output_dir) 
    for issue in issue_list:
        #print('processing issue:\n{}'.format(issue))
        file_name = '{}_{}.md'.format(issue.id, normalize_issue_title(issue.title))
        with open('{}{}{}'.format(output_dir, os.sep, file_name), 'w+') as md:
            write_hugo_header(md, issue)
            write_hugo_body(md, issue)


def are_dirs_same(dir1, dir2):
    dirs_cmp = filecmp.dircmp(dir1, dir2)

    if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or len(dirs_cmp.funny_files) > 0:
        print('has left/right only entry(ies)...')
        return False

    (_, mismatch, errors) =  filecmp.cmpfiles(dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch) > 0 or len(errors) > 0:
        print('has mismatch or error')
        return False

    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not are_dirs_same(new_dir1, new_dir2):
            return False
    return True


def generate_site():
    has_changed = False

    public_dir = 'public'
    public_dir_prev = 'public.prev'
    if os.path.isdir(public_dir):
        # rename previous public folder
        if os.path.isdir(public_dir_prev):
            shutil.rmtree(public_dir_prev, True)
        shutil.move(public_dir, public_dir_prev)
        # remove .git dir
        shutil.rmtree('{}{}.git'.format(public_dir_prev, os.sep), True)
    else:
        print('no previous build...')
        has_changed = True

    subprocess.run('/usr/local/bin/hugo')

    # compare public folder with previous public
    if has_changed:
        return True
    else:
        return not are_dirs_same(public_dir, public_dir_prev)


def deploy():
    # clone repo
    repo_dir = 'jrdeng.github.io'
    if os.path.isdir(repo_dir):
        shutil.rmtree(repo_dir, True)
    subprocess.run('git clone git@github.com:jrdeng/jrdeng.github.io.git {}'.format(repo_dir).split(' '))

    # move '.git' to 'public', so we make 'public' as the new repo
    shutil.move('{}{}.git'.format(repo_dir, os.sep), 'public')

    # remove the useless repo
    shutil.rmtree(repo_dir, True)
    
    # deploy the new repo
    cwd = os.getcwd() # >>>>>>>>>>>
    os.chdir('public')
    subprocess.run('git status'.split(' '))
    subprocess.run('git add .'.split(' '))
    now = datetime.now()
    now_str = str(now)[:19]
    subprocess.run(['git', 'commit', '-m', 'rebuild site {}'.format(now_str)])
    subprocess.run('git push'.split(' '))
    os.chdir(cwd) # <<<<<<<<<<

    # keep 'public' in local for test ('public' should be in .gitignore, and we will remove it before next generating)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ht:o:r:', ['help', 'token=', 'owner=', 'repo='])
    except getopt.GetoptError as err:
        print(err)
        usage()
        exit(2)
    token = None                # must be set
    owner = 'jrdeng'            # default owner
    repo = 'jrdeng.github.io'   # default repository
    for o, a in opts:
        if o == '-h':
            usage()
            exit()
        elif o in ('-t', '--token'):
            token = a
        elif o in ('-o', '--owner'):
            owner = a
        elif o in ('-r', '--repo'):
            repo = a
        else:
            usage()
            assert False, 'unhandled option'
    if token is None:
        print('token is not specified, try to get it from ENV...')
        token_env = 'GITHUB_GQL_TOKEN'
        try:
            token = os.environ[token_env]
        except KeyError as err:
            print('{} is not in ENV? exit.'.format(token_env))
            exit(2)

    # fetch issues from github
    print('fetching issues from github...')
    issue_list = fetcher.fetch_issues(token, owner, repo)
    issue_num = len(issue_list)
    print('issue_num: {}'.format(issue_num))

    if issue_num == 0:
        print('fetch_issues() returned empty!')
        exit(1)

    # switch working dir >>>>>>>>>>
    cwd = os.getcwd()
    os.chdir(blog_dir)

    # generate markdown files for hugo
    print('generating markdown files for hugo...')
    generate_md(issue_list, 'content/post')

    # generate static website
    print('generating static website...')
    has_changed = generate_site()

    # deploy to github
    if has_changed:
        print('deploying new website to github...')
        deploy()
    else:
        print('website not changed, just ignore.')

    # switch back workding dir <<<<<<<<<<
    os.chdir(cwd)


if __name__ == '__main__':
    main()
    print('\nDone!\n')

