#!/usr/bin/env python3

# recrep.py - recursive replace

from __future__ import print_function
from optparse import OptionParser
import os


def mod_files(files, original, replacement):
    '''change the files - returns set of changed filenames'''
    changed_files, error_files = set(), set()
    for f in files:
        pass


def display_files(files, changed_files, error_files):
    '''display changed & unchanged files'''
    if not files:
        print("No files found")
        return
    if files:
        print("Files found but unchanged:")
        print(files.difference(changed_files))
    if changed_files:
        print("Files found & changed:")
        print(changed_files)
    if changed_files:
        print("Files found & returned error:")
        print(error_files)


def rec_files(exc_fnmatch, inc_fnmatch, inc_git = False, startdir = '.'):
    '''return set of all files under dir, taking filters into account'''
    # os.walk better than glob as includes hidden & normal folders
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(startdir)
             for f in filenames]
    if not inc_git:
        # exclude files under .git directories
        gitdir = os.path.join(".git","")
        files = [f for f in files if gitdir not in f]
    return set(files)


def main():
    parser = OptionParser()
    parser.add_option("--include-git", action="store_true",
                      dest="inc_git",
                      help="include git dirs (not recommended)")
    parser.add_option("--exclude", dest="exc_fnmatch",
                      help="wildcards to exclude")
    parser.add_option("--include", dest="inc_fnmatch",
                      help="wildcards to include")
    (options, args) = parser.parse_args()
    myfiles = rec_files(options.exc_fnmatch, options.inc_fnmatch,
                        options.inc_git)
    display_files(myfiles, set())


if __name__ == "__main__":
    main()
