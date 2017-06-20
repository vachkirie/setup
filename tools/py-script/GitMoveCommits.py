#!/usr/bin/python

import sys, getopt
import os
import git
import logging
import copy
from itertools import tee, islice, chain, izip
from subprocess import call
from os.path import expanduser


log_file = '.GitSplit.log'
home = expanduser("~")


#
#------------------------------------------------------------------------------
#  Short commit id
#------------------------------------------------------------------------------
#
def Sid(cid):
        #if cid == None: return 'None'
        return cid[:10]


#
#------------------------------------------------------------------------------
# Git functions
#------------------------------------------------------------------------------
#
def CherryPick(repo, c):
    try:
        repo.git.cherry_pick(c, '--ff')

    except Exception:
        return False
    else:
        return True


#
#------------------------------------------------------------------------------
# list commitIDs from a to b
#------------------------------------------------------------------------------
#
def gitGetCommitList(repo,a,b,path):
    cpath = []
    commitIDs = []
    clist_strip = []
    text = repo.git.rev_list('%s..%s' % (a,b), '--', path).split("\n")
    commitIDs.extend(text)

    logging.debug('gitGetCommitList: list between %s and %s in %s' % (a,b,path))
    for commit in commitIDs:
        logging.debug('gitGetCommitList:   %s' % (commit))

    commitIDs.reverse()

    if path == '.':
        return commitIDs

    for c in commitIDs:
        cpath = getCommitDomain(c)
        if cpath != None:
            if cpath['path'] == path:
                clist_strip.append(c)
                logging.debug('gitGetCommitList:     keep %s from %s' % (c,path))
            else:
                logging.debug('gitGetCommitList:     discard %s from %s (%s)' % (c,path,cpath['path']))

    return clist_strip



#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
#

def FileWrite(fname, msg):
    f = open('fmsg', "w")
    f.write( msg )
    f.close()

#
#------------------------------------------------------------------------------
# Logging functions
#------------------------------------------------------------------------------
#
def LogCpGeneric(prefix, commit, head_sha, summary, flist=[], dlist=[]):

    print '   %s %s --> %s %s' % (prefix, Sid(commit), Sid(head_sha),summary)
    logging.info('   %s %s --> %s %s' % (prefix, Sid(commit), Sid(head_sha),summary))

    if len(dlist) != 0:
        logging.info('       Modified %d domains' % (len(dlist)))
        for d in dlist:
            logging.info('           %s' % (d))

    if len(flist) != 0:
        logging.info('       Modified %d files' % (len(flist)))
        for f in flist:
            logging.info('           %s' % (f))





def RangeParse(s):
    if len(s) == 0:
        return None, None

    temp = s.replace(".."," ").split()
    return temp[0], temp[1]


def LogConsoleAndFile(string):
    print string
    logging.info('%s' % string)


#
#------------------------------------------------------------------------------
# Print Help
#------------------------------------------------------------------------------
#
def LogHelp():
    print 'GitHeaderPrefix.py --range <id>..<id> --prefix <commitid>'
    print ''
    print '     --range       : whole commit range'
    print '     --exclude     : exclusion commit range'
    print '     --json        : specify json file'
    print ''
    print 'Example:'
    print '     $ GitHeaderPrefix.py --range HEAD~15..HEAD~10 --top <tag> --prefix [GOOGLE]'
    print ''

    print ' [ ]: Straigth cherry-pick'
    print ' [-]: Straigth cherry-pick of an undefined domain'
    print ' [R]: Reordered'
    print ' [U]: Unsplit'
    print ' [E]: Generic error'
    print ' [X]: Excluded'
    print ' [C]: Conflict'

# GitHeaderPrefix.py --range 2bb84bc..ff67c64 --top temp --prefix '[GOOGLE 4.4] '

###############################################################################
#
# Main
#
###############################################################################


start = ''
end = ''
base = ''
prefix = ''
FinalLog = ''
range_work = ''

verbose=False
interactive = False

# enable logging
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)

# Get options
try:
   opts, args = getopt.getopt(sys.argv[1:],"hivsr",["interactive","verbose","base=","range="])
except getopt.GetoptError:
   LogHelp()
   sys.exit(0)

for opt, arg in opts:
    if opt == '-h':
        LogHelp()
        sys.exit()
    elif opt in ("-g", "--range"):
        range_work = arg
    elif opt in ("-t", "--base"):
        base = arg
    elif opt in ("-p", "--prefix"):
        do_strip = False
        prefix = arg
    elif opt in ("-s", "--strip"):
        do_strip = True
        prefix = arg
    else:
        print 'Unknown option %s' % opt
        LogHelp()


if len(base) == 0:
    print 'WARNING: missing top parameter'
    sys.exit(0)

if len(range_work) == 0:
    print 'WARNING: missing range parameter'
    sys.exit(0)

repo = git.Repo(".")

# Check untracked files
flist_untracked = repo.untracked_files
if len(flist_untracked) != 0:
    print 'WARNING: Please remove untracked files:'
    for f in flist_untracked:
        print '     %s' % f
    sys.exit(0)

if repo.is_dirty():
    print 'WARNING: Modified files:'
    sys.exit(0)

# init head commits
start, end = RangeParse(range_work)

def IsGoogleCommit(repo, c)
    sum = repo.commit(c).summary

    return sum.startswith(d['[GOOGLE'])

#------------------------------------------------------------------------------
# Proceed
#------------------------------------------------------------------------------
clist_movable = []
clist_moved = []

LogConsoleAndFile('\n')
LogConsoleAndFile('Add %s to Commits from %s..%s' % (prefix, start, end))


repo = git.Repo(".")
# list commits from A to B
clist_global = gitGetCommitList(repo, base, end, '.')
clist_movable = gitGetCommitList(repo, start, end, '.')

# initialize source to baseline
repo.git.checkout(base, '-f')

# for each movable commit, try to apply on base.
# if fails, skip
for c in clist_movable:

    if IsGoogleCommit(repo, c)
        LogCpGeneric('[U] GOOGLE    --- ', c, '', repo.commit(c).summary)
        continue

    if CherryPick(repo, c) == False:
        # cherry-pick failed likely due to a conflict
        LogCpGeneric('[C] SKIPPED    --- ', c, '', repo.commit(c).summary)
        #logging.info( os.system('git status')
        os.system('git reset -q HEAD')
        os.system('git checkout -- .')
        os.system('git clean -fd')
    else:
        LogCpGeneric('[ ]', c, repo.head.commit.hexsha, repo.head.commit.summary)
        clist_moved.append(c)
        clist_global.remove(c)

new_base = repo.head.commit.hexsha

print 'git rebase --onto %s %s %s' % (Sid(repo.head.commit.hexsha), base, end)
# for each remainng commit, try to cherry-pick
for c in clist_global:
    if CherryPick(repo, c) == False:
        LogCpGeneric('[X] SKIPPED    --- ', c, Sid('xxxxxxxxxxxxx'), repo.commit(c).summary)
    else:
        LogCpGeneric('[ ]', c, repo.head.commit.hexsha, repo.head.commit.summary)

LogConsoleAndFile('')

print '%s..%s - %d commits moved to base' % (base, Sid(new_base), len(gitGetCommitList(repo, base, new_base, '.')))
print 'base: %s..%s' % (base, Sid(new_base))
print 'top : %s..%s' % (end, Sid(repo.head.commit.hexsha))


#print 'git rebase --onto %s %s %s' % (Sid(repo.head.commit.hexsha), base, end)
#os.system('git rebase --onto %s %s %s' % (repo.head.commit.hexsha, base, end))

LogConsoleAndFile('git diff --name-status %s..%s' % (end, Sid(repo.head.commit.hexsha)))
os.system('git diff --name-status %s..%s' % (end, repo.head.commit.hexsha))


print 'Moved %d commits from %s..%s to base(%s)' % (len(clist_moved), start, end, base)

print '\nbase     range %s..%s' % (Sid(start),Sid(end))
print 'reworked range %s..%s' % (Sid(start),Sid(repo.head.commit.hexsha))

LogConsoleAndFile('')


LogConsoleAndFile(FinalLog)

