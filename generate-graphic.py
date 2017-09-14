#!/usr/bin/env python3

import datetime
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

def execute_git_command(command):
    os.chdir('styles')
    command_output = subprocess.getoutput('git ' + command)
    os.chdir('..')

    return command_output

def delete_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)

def prepare_repository():
    delete_directory('styles')
    os.system('git clone -q https://github.com/citation-style-language/styles-distribution styles')

def get_repository_commits():
    os.chdir('styles')
    commits = subprocess.getoutput('git rev-list master')
    os.chdir('..')
    commitsList = commits.split('\n')
    commitsList.reverse()

    return commitsList

def count_styles_from_list(git_output):
    independent_styles = 0
    dependent_styles = 0
    total = 0
    for line in git_output.split('\n'):
        if not '.csl' in line:
            continue

        if line.startswith('dependent/') == False:
            independent_styles += 1

        total +=1

    dependent_styles = total - independent_styles
    
    return (total, independent_styles, dependent_styles)

def get_date_from_commit(commit):
    date_git = execute_git_command('show -s --format="%%ci" %s' % (commit))

    date_git = date_git.rstrip("\n")

    if date_git == '':
        # git show doesn't return anything useful?
        return None

    date = datetime.datetime.strptime(date_git, "%Y-%m-%d %H:%S:%M %z")

    return date.strftime('%Y-%m-%d')

def count_styles(commit):
    out = execute_git_command('ls-tree -r --name-only %s' % (commit))
    (total, independent_styles, dependent_styles) = count_styles_from_list(out)

    return (total, independent_styles, dependent_styles)

def update_template(fileName, values):
    text = open(fileName + '.tmpl','r').read()

    for key in values.keys():
        text = text.replace('%' + key + '%', str(values[key]))

    f = open(OUTPUT_DIRECTORY + '/' + fileName, 'w')
    f.write(text)
    f.close()

def create_csv_styles(commits):
    shutil.copy('output.csv', OUTPUT_DIRECTORY)
    file = open(OUTPUT_DIRECTORY + '/output.csv', 'a')

    for i in range(len(commits)):
        date = get_date_from_commit(commits[i])
        if date == None or date < '2014-02-12':
            continue

        if i < range(len(commits))[-1]:
            nextDate = get_date_from_commit(commits[i+1])
            if date == nextDate:
                continue

        (total, independent_styles, dependent_styles) = count_styles(commits[i])

        if date not in days_to_skip:
            file.write('%s,%s,%s,%s\n' % (date, total, independent_styles, dependent_styles))

    file.close()

if __name__ == '__main__':
    prepare_repository()
    delete_directory(OUTPUT_DIRECTORY)
    os.makedirs(OUTPUT_DIRECTORY)

    commits = get_repository_commits()
    create_csv_styles(commits)
    last_commit = commits[-1]

    (total, independent_styles, dependent_styles) = count_styles(last_commit)

    update_template('index.html',
        {'LAST_UPDATE': datetime.datetime.utcnow().strftime("%Y/%m/%d"),
        'TOTAL_STYLES': total, 'UNIQUE_STYLES' : independent_styles, 'DEPENDENTS' : dependent_styles})
