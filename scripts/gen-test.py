#!/usr/bin/env python3

"""
Generate a unit test file and its baseline for a given matcher
"""

import argparse
import os
import sys
import re
import subprocess
import shutil

def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-m',
        '--matcher',
        required=True,
        type=str,
        help='matcher string ID')

    parser.add_argument(
        '-l',
        '--log',
        nargs='?',
        type=str,
        default='sbcodexform.log',
        help='log file name')
    
    parser.add_argument(
        'input',
        type=str,
        nargs=1,
        help='input file for baseline generation')
    
    args = parser.parse_args()
    logname = args.log
    matcher = args.matcher

    file = args.input[0]
    file = os.path.abspath(file)
    dirname, filename = os.path.split(file)
    root_name = 'clang-xform'
    root = os.path.join(dirname[:dirname.find(root_name)-1], root_name)
    dir_rel = dirname[dirname.find(root_name):]
    dir_rel = os.path.relpath(dir_rel, root_name)
    
    script_dir = os.path.dirname(__file__);
    template = os.path.join(script_dir, 'template/TestTemplate.cpp')

    # generate gtest file
    file_data = None
    with open(template, "r") as f:
        file_data = f.read()
        # replace with the matcher name provided by the user
        file_data = file_data.replace('__NAME__', matcher)
        file_data = file_data.replace('__PATH__', dir_rel)
        file_data = file_data.replace('__FILE__', filename)
        file_data = file_data.replace('__LOG__', logname)

    # write the data into tmatcher.cpp
    new_file = os.path.join(dirname, 't' + matcher + '.cpp')
    print('generating ' + new_file)
    with open(new_file, "w") as f:
        f.write(file_data)

    # generate baseline
    # make a copy of the original file
    file_copy = os.path.join(dirname, filename + '.tmp')
    shutil.copyfile(file, file_copy)

    # generate compilation database for the file
    json_file = os.path.join(dirname, 'compile_commands.json') 
    print('generating ' + json_file)
    # read template file
    template = os.path.join(root, 'scripts', 'template', 'compile_commands.json')
    template_data = None
    with open(template, "r") as f:
        template_data = f.read()
        # replace the directory name and file name
        template_data = template_data.replace('__DIRECTORY__', dirname)
        template_data = template_data.replace('__FILE__', filename)

    # write the data into dirname path
    with open(json_file, "w") as f:
        f.write(template_data)

    # generating new baselines
    log = os.path.join(dirname, logname)
    file_gold = os.path.join(dirname, filename + '.gold')
    log_gold = os.path.join(dirname, logname + '.gold')
    
    print('generating ' + log_gold)
    print('generating ' + file_gold)
    cmd = root + '/bin/clang-xform -m ' + matcher + ' -l ' + log + ' -q ' + file
    process = subprocess.run(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    
    # remove old baseline if already exists
    if os.path.exists(file_gold):
        os.remove(file_gold)
    if os.path.exists(log_gold):
        os.remove(log_gold)

    # rename generated files into baselines
    os.rename(file, file_gold)
    os.rename(log, log_gold)
    os.rename(file_copy, file)

    # adjust log baseline by removing attributes info
    lines = None
    with open(log_gold, "r") as f:
        lines = f.readlines()
    with open(log_gold, "w") as f:
        for line in lines:
            if line.startswith('No.'):
                line = line[line.rfind('|') + 2:]
            f.write(line)
        
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
