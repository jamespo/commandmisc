#!/usr/bin/env python3

# recrep.py - recursive replace

from __future__ import print_function
from optparse import OptionParser
from tempfile import NamedTemporaryFile
from shutil import copyfile
import os


def mod_file(myfile, original, replacement):
    '''modify file - make copy and overwrite'''
    file_modified, file_in_error = False, False
    try:
        with open(myfile) as f, \
             NamedTemporaryFile(delete=False) as w:
            for inline in f:
                newline = inline.replace(original, replacement)
                if newline != inline:
                    file_modified = True
                w.write(newline.encode())
    except:
        file_in_error = True
    # copy over if modified
    if file_modified and not file_in_error:
        try:
            copyfile(w.name, myfile)
        except:
            # copy failed
            file_modified = False
            file_in_error = True
    os.remove(w.name)
    return file_modified, file_in_error

    
def mod_files(files, original, replacement):
    '''change the files - returns set of changed filenames'''
    changed_files, error_files = set(), set()
    for f in files:
        file_modified, file_in_error = mod_file(f, original, replacement)
        if file_modified:
            changed_files.add(f)
        if file_in_error:
            error_files.add(f)
    return changed_files, error_files


def format_files(files):
    '''format list of files for printing'''
    return "\n".join(files)


def display_files(files, changed_files, error_files):
    '''display changed & unchanged files'''
    if not files:
        print("No files found")
        return
    if files:
        print("Files found but unchanged:")
        print(format_files(files.difference(changed_files)))
    if changed_files:
        print("Files found & changed:")
        print(format_files(changed_files))
    if error_files:
        print("Files found & returned error:")
        print(format_files(error_files))


def rec_files(exc_fnmatch, inc_fnmatch, inc_git=False, startdir='.'):
    '''return set of all files under dir, taking filters into account'''
    # os.walk better than glob as includes hidden & normal folders
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(startdir)
             for f in filenames]
    if not inc_git:
        # exclude files under .git directories
        gitdir = os.path.join(".git", "")
        files = [f for f in files if gitdir not in f]
    # TODO: apply inc & exc filters
    return set(files)


def getopts():
    '''parse command line args'''
    parser = OptionParser()
    parser.add_option("--include-git", action="store_true",
                      dest="inc_git",
                      help="include git dirs (not recommended)")
    parser.add_option("--exclude", dest="exc_fnmatch",
                      help="wildcards to exclude")
    parser.add_option("--include", dest="inc_fnmatch",
                      help="wildcards to include")
    parser.add_option("-o", "--original", dest="orig",
                      help="text to match")
    parser.add_option("-r", "--replacement", dest="repl",
                      help="text to replace with")
    parser.add_option("-n", "--dry-run", dest="dryrun", action="store_true",
                      help="don't change files")
    (options, args) = parser.parse_args()
    return options


def main():
    options = getopts()
    myfiles = rec_files(options.exc_fnmatch, options.inc_fnmatch,
                        options.inc_git)
    if options.dryrun:
        display_files(myfiles, set(), set())
    else:
        changed_files, error_files = mod_files(myfiles, options.orig,
                                               options.repl)
        display_files(myfiles, changed_files, error_files)


if __name__ == "__main__":
    main()
