#!/usr/bin/python

import commands
import datetime
import dateutil.parser
import glob
import os
import shutil
import subprocess
import time
import shutil

# Script that fetches https://github.com/citation-style-language/styles and does a quick report
# of the number of styles.

# Where the Web will be saved
OUTPUT_DIRECTORY='output/'

# Ignores these days because for some reason git shows a smaller number of files (even though
# for some of them I haven't found any reason).
days_to_skip = ['2013-11-02']
# To avoid this: see http://stackoverflow.com/questions/5720343/using-git-show-all-commits-that-exist-only-on-one-specific-branch-and-not-a . Didn't work but should try again.

def execute_git_command(command):
    os.chdir('styles')
    command_output = commands.getoutput('git ' + command)
    os.chdir('..')

    return command_output

def delete_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)

def prepare_repository():
    delete_directory('styles')
    os.system('git clone -q https://github.com/citation-style-language/styles')

def get_repository_commits():
    os.chdir('styles')
    commits = commands.getoutput('git rev-list --author="\(rmzelle\)\|\(adam3smith\)\|\(Arcus\)" master')
    os.chdir('..')
    commitsList = commits.split('\n')
    commitsList.reverse()

    return commitsList

def count_styles_from_list(git_output):
    unique_styles = 0
    total = 0
    for line in git_output.split('\n'):
        if not '.csl' in line:
            continue

        if line.startswith('dependent/') == False:
            unique_styles += 1

        total +=1

    return (total,unique_styles)

def get_date_from_commit(commit):
    date_git = execute_git_command('show -s --format="%%ci" %s' % (commit))

    date_git = date_git.rstrip("\n")

    if date_git == '':
        # git show doesn't return anything useful?
        return None

    date = dateutil.parser.parse(date_git)

    return date.strftime('%Y-%m-%d')

def count_styles(commit):
    out = execute_git_command('ls-tree -r --name-only %s' % (commit))
    (total, UniqueStlyes) = count_styles_from_list(out)

    return (total, UniqueStlyes)

def update_template(fileName, values):
    text = open(fileName + '.tmpl','r').read()

    for key in values.keys():
        text = text.replace('%' + key + '%', str(values[key]))

    f = open(OUTPUT_DIRECTORY + '/' + fileName, 'w')
    f.write(text)
    f.close()

def create_csv_styles(commits):
    file = open(OUTPUT_DIRECTORY + '/output.csv', 'w')
    file.write('Date,Total,Unique\n')

    lastDate = 0
    for commit in commits:
        date = get_date_from_commit(commit)
        if date == None or date < '2011-03-03':
            continue

        (total, unique_styles) = count_styles(commit)

        if lastDate != date:
            if date not in days_to_skip:
                file.write('%s,%s,%s\n' % (date,total,unique_styles))
        
        lastDate = date

    file.close()

if __name__ == '__main__':
    prepare_repository()
    delete_directory(OUTPUT_DIRECTORY)
    os.makedirs(OUTPUT_DIRECTORY)

    commits = get_repository_commits()
    create_csv_styles(commits)
    last_commit = commits[-1]

    (total, unique_styles) = count_styles(last_commit)

    update_template('index.html',
        {'LAST_UPDATE': "%s, %s" % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), last_commit),
        'TOTAL_STYLES': total, 'UNIQUE_STYLES' : unique_styles})
    shutil.copy('dygraph-combined.js', OUTPUT_DIRECTORY)
