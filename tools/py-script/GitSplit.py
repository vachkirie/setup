#!/usr/bin/python

import sys, getopt
import os
import json
import git
import logging
import copy
import subprocess
from itertools import tee, islice, chain, izip
from subprocess import call
from os.path import expanduser


log_file = '.GitSplit.log'
home = expanduser("~")
json_file = home+'/kernel_domains.json'


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
#  Shell
#------------------------------------------------------------------------------
#
def ShellCmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return output

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

def CheckRepoIsClean():
    if repo.is_dirty():
        print 'WARNING: Modified files:'
        print ShellCmd('git status')
        if AskYn('Remove staged changes ?') == False:
            print ' Aborting ...'
            sys.exit(0)
        else:
            os.system('git reset -q HEAD')
            os.system('git checkout -- .')

    # Check untracked files
    flist_untracked = repo.untracked_files
    if len(flist_untracked) != 0:
        LogConsoleAndFile('WARNING: Please remove untracked files:')
        for f in flist_untracked:
            LogConsoleAndFile('     %s' % f)
        if AskYn('Remove untracked files ?') == False:
            LogConsoleAndFile(' Aborting ...')
            sys.exit(0)
        else:
            os.system('git clean -fd')
            flist_untracked = repo.untracked_files
            if len(flist_untracked) != 0:
                for f in flist_untracked:
                    LogConsoleAndFile('     %s' % f)
                LogConsoleAndFile(' Aborting ...')
                sys.exit(0)



tab = []
idx=0
def GitLogSummary(repo, base, top):
    found = False
    output=''

    for i in tab:
        if (i[0] == base) and (i[1] == top):
            found = True
            output = i[2]

    cmd = 'git log --pretty=format:"%s" '+base+'..'+top

    if found == False:
        output = ShellCmd(cmd)
        output = output.split("\n")

    if found == False:
        tab.append([base, top, output])
        logging.info(('tab new entry %d [%s, %s]' % (len(tab), base, top)))

    return output


def FindSummaryInLog(repo, base, top, sum):
    output = GitLogSummary(repo, base, top)

    sum = repr(sum)
    if len(output)>1:
        for i in output:
            if repr(i) == sum: return True
        return False
    else:
        return False


def CountPatternInLog(repo, pattern, base, top):
    pattern = repr(pattern)
    cmd = 'git log --oneline '+base+'..'+top+' | grep -F '+pattern
    output = ShellCmd(cmd)
    return len(output.split("\n"))-1



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


def gitGetCommitSha(repo,c):
        list = gitGetCommitList(repo, c+'~', c, '.')
        return list[0]

#
#------------------------------------------------------------------------------
# list file changed between a and b
#------------------------------------------------------------------------------
#
def gitDiffFiles(repo,a,b):
    logging.debug('gitDiffFiles(%s, %s)' % (a,b))
    flist = []
    differ = repo.git.diff('%s..%s' % (a,b), '--name-only').split("\n")
    flist.extend(differ)
    return flist


#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
#
def gitAmendMsg(repo, message):
    message = 'git commit --amend -q -m' +'"' + message +'"'
    os.system(message.encode('utf-8'))

#
#------------------------------------------------------------------------------
# get file domain if any
#------------------------------------------------------------------------------
#
def getFileDomain(filepath):
    domain = None

    for d in json_domainlist:
        if filepath.startswith(d['path']) == True:
            if domain == None: # if no domain found yet
                domain = d
            elif(len(domain['path']) < len(d['path'])): # if closest subdomain found
                domain = d

    return domain


def GetDomainsFromFlist(flist):
    dlist = []
    flist_unknown = []
    logging.debug('GetDomainsFromFlist()')
    # look for a domain
    for f in flist:
        if FileIsWildcard(f) == True:
            continue

        domain = getFileDomain(f)
        if domain == None : # check if file belong to a domain
            domain = unknown_domain
            flist_unknown.append(f)

        if domain not in dlist:
            dlist.append(domain)

    if unknown_domain in dlist:
        dlist.remove(unknown_domain)
        dlist.append(unknown_domain)

    # if only one domain and wildcards, remove unknown domain from list
    for f in flist_unknown:
        if FileIsWildcard(f) == False:
            return dlist

    if unknown_domain in dlist:
        dlist.remove(unknown_domain)
    return dlist


def GetDomainsFromCommit(repo, commit):
    logging.debug('GetDomainsFromCommit(%s)' % (commit))
    filelist = GetFlistFromCommit(repo, commit) # list files modified
    dlist = GetDomainsFromFlist(filelist)
    return dlist

def GetFlistFromCommit(repo, c):
    return gitDiffFiles(repo, c + '~', c)


#
#------------------------------------------------------------------------------
# get file domain if any
#------------------------------------------------------------------------------
#
def getCommitDomain(commit):
    domain = None
    templist = []
    logging.debug('getCommitDomain(%s)' % (commit))

    flist = gitDiffFiles(repo, commit+'~', commit) # list files modified

    for f in flist:
        if FileIsWildcard(f) == False:
            templist.append(f)

    for f in templist:
        for d in json_domainlist:
            if f.startswith(d['path']) == True:
                if domain == None: # if no domain found yet
                    domain = d
                elif(len(domain['path']) < len(d['path'])): # if closest subdomain found
                    domain = d


    for f in flist:
        logging.debug('getCommitDomain:     %s' % (f))
    logging.debug('getCommitDomain: returns %s' % (domain))

    return domain




#
#------------------------------------------------------------------------------
# get file domain if any
#------------------------------------------------------------------------------
#
def getFlistDomain(flist):
    domain = unknown_domain
    templist = []
    logging.debug('getFlistDomain()')
    for f in flist:
        if FileIsWildcard(f) == False:
            templist.append(f)

    for f in templist:
        for d in json_domainlist:
            if f.startswith(d['path']) == True:
                if domain == unknown_domain: # if no domain found yet
                    domain = d
                elif(len(domain['path']) < len(d['path'])): # if closest subdomain found
                    domain = d

    logging.debug('getFlistDomain: returns %s' % (domain))
    return domain


#
#------------------------------------------------------------------------------
# get domain option value
#------------------------------------------------------------------------------
#
def getDomainOption(dom, option):
    opts=dom['options']
    ret = opts.find(option)
    if opts.find(option) >= 0:
        #print '%s option %s found' % (dom['path'], option)
        return True

    #print '%s option %s not found' % (dom['path'], option)
    return False

def getDomListOption(dlist, option):
    for d in dlist:
        if getDomainOption(d, option) == True:
            return True

    return False



def NextItem(l, cur):
   i=l.index(cur)
   return l[i+1] if i<len(l)-1 else None


def ListStripList(la, lb):
    for i in lb:
        if i in la:
            logging.debug(' ListStripList remove %s' % i)
            la.remove(i)

#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
#
def FileIsInDomain(f,dpath):
    d = getFileDomain(f)

    if d != None and dpath == d['path']:
        return True
    if d == None and dpath == 'unknown':
        return True

    return False


#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
#
def FileIsWildcard(f):

    for w in json_domainwildcard:
        if w['options'].find('startswith') >= 0:
            if f.startswith(w['path']) == True:
                #print 'wildcard: %s startswith %s' % (f,w['path'])
                return True

        elif f.find(w['path']) >= 0:
                #print 'wildcard: %s contains %s' % (f,w['path'])
                return True

    return False

#
#------------------------------------------------------------------------------
# Return list of file which does not belong to the domain
#------------------------------------------------------------------------------
#
def FilterOutDomain(flist, domain):
    stripflist = []
    logging.debug('FilterOutDomain(%s)' % (domain))

    for f in flist:
        if FileIsInDomain(f,domain) == True:
            logging.debug('FilterOutDomain:    remove D %s' % (f))
        elif FileIsWildcard(f):
            logging.debug('FilterOutDomain:    remove W %s' % (f))
        else:
            logging.debug('FilterOutDomain:    keep %s' % (f))
            stripflist.append(f)

    return stripflist

#
#------------------------------------------------------------------------------
# Return list of files which belongs to the domain
#------------------------------------------------------------------------------
#
def FilterInDomain(flist, dpath):
    stripflist = []

    for f in flist:
        if FileIsInDomain(f,dpath) == True:
            logging.debug('FilterInDomain:    %s in %s' % (f, dpath))
            stripflist.append(f)
        elif (FileIsInDomain(f,'unknown') == True) and (FileIsWildcard(f) == True):
            logging.debug('FilterInDomain:    %s in %s (wildcard)' % (f, dpath))
            stripflist.append(f)
        else:
            logging.debug('FilterInDomain:    %s is not in %s' % (f, dpath))

    return stripflist


#
#------------------------------------------------------------------------------
# Logging functions
#------------------------------------------------------------------------------
#
def LogConsoleAndFile(string):
    print string
    logging.info('%s' % string)

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



def LogSplitResult(repo,commit,domain, flist_merged, flist_remaining):
    prefix_split = '   [S] '
    # print prefix_split+'split for %s' % (domain)
    logging.info(prefix_split+'split for %s' % (domain))

    print prefix_split+'           --> %s %s' % (Sid(repo.head.commit.hexsha),repo.head.commit.summary)
    logging.info(prefix_split+'           --> %s %s' % (Sid(repo.head.commit.hexsha),repo.head.commit.summary))

    if verbose == True: print prefix_split+'Merged files %d' % (len(flist_merged))
    logging.info(prefix_split+'Merged files %d' % (len(flist_merged)))
    for f in flist_merged:
        if verbose == True: print prefix_split+'   %s' % (f)
        logging.info(prefix_split+'   %s' % (f))

    if verbose == True: print prefix_split+'Remaining files %d' % (len(flist_remaining))
    logging.info(prefix_split+'Remaining files %d' % (len(flist_remaining)))
    for f in flist_remaining:
        if verbose == True: print prefix_split+'   %s' % (f)
        logging.info(prefix_split+'   %s' % (f))

    if verbose == True: print prefix_split
    logging.info('')


def LogSplit(commit, summary, flist):
   logging.info('\n')
   logging.info('Split: %s %s' % (Sid(commit),repo.head.commit.summary))
   print 'Split: %s %s' % (Sid(commit),repo.head.commit.summary)
   logging.info('       Modified %d files' % (len(flist)))
   for f in flist:
       logging.info('           %s' % (f))


def LogReorderPrepare(domain, clist_domain, clist_merged):
    print '       Reorder %d commits in domain %s' % (len(clist_domain),domain['path'])
    logging.info('       Reorder %d commits in domain %s' % (len(clist_domain),domain['path']))
    logging.debug('      ---------------------------------')
    for c in clist_domain:
        if c in clist_merged:
            logging.debug('      %s merged' % Sid(c))
        else:
            logging.debug('      %s' % Sid(c))

    logging.debug('      ---------------------------------')


def RangeParse(s):
    if len(s) == 0:
        return None, None

    temp = s.replace(".."," ").split()
    return temp[0], temp[1]


def LogCommitRange(msg, rev_a, rev_b):
    clist = gitGetCommitList(repo, rev_a, rev_b, '.')
    crange = '%s %s..%s - %d commits' % (msg, rev_a, rev_b, len(clist))
    LogConsoleAndFile('%s' % (crange))

def LogOp(msg, in_a, in_b, in_es, in_ee, out_a, out_b, out_es, out_ee):
    if in_es == None or in_ee == None or out_es == None or out_ee == None:
        ilist = gitGetCommitList(repo, in_a, in_b, '.')
        olist = gitGetCommitList(repo, out_a, out_b, '.')
        crange = '%s %s..%s - %d commits ---> %s..%s - %d commits' % (msg, in_a, in_b, len(ilist), out_a, out_b, len(olist))
    else:
        ilist = gitGetCommitList(repo, rev_a, rev_b, '.')
        olist = gitGetCommitList(repo, rev_a, rev_b, '.')
        crange = '%s %s..%s - %d commits ---> %s..%s - %d commits' % (msg, in_a, in_b, len(ilist), out_a, out_b, len(olist))
        crange = '%s %s..%s - %d commits ---> %s..%s - %d commits' % (msg, in_a, in_b, len(ilist), out_a, out_b, len(olist))
    return crange



#
#------------------------------------------------------------------------------
# Marks
#------------------------------------------------------------------------------
#
def IsMarkedRight(v, s):
    if s.startswith('[') and (v in s):
        return True
    else:
        return False

def IsMarked(s):
    for m in json_marklist:
        for sm in m:
            if s.startswith(sm['mark']): return True
    return False


def RemoveMark(s):
    for m in json_marklist:
        for sm in m:
            s = s.replace(sm['mark'],'')
    return s


def GetMarkVersion(repo, c):
    version = ''
    sum = str(repo.commit(c).summary)
    sum = RemoveMark(sum)
    for m in json_marklist:
        for sm in m:
            if FindSummaryInLog(repo, sm['base'], sm['top'], str(sum)):
                version += str(sm['mark'])
                break
    return version



#
#------------------------------------------------------------------------------
# Filesystem
#------------------------------------------------------------------------------
#
def FileWrite(fname, msg):
    f = open('fmsg', "w")
    f.write( msg )
    f.close()

#
#------------------------------------------------------------------------------
# Interactive functions
#------------------------------------------------------------------------------
#
def AskYn(msg):
    str = raw_input('%s (Y/n)' % msg)
    logging.info('User Choice: %s' % (str))
    if (str == 'n') or (str == 'N'):
        return False
    else:
        return True

def AskyN(msg):
    str = raw_input('%s (y/N)' % msg)
    logging.info('User Choice: %s' % (str))
    if (str == 'y') or (str == 'Y'):
        return True
    else:
        return False

def AskString(msg):
    str = raw_input('%s' % msg)
    logging.info('User Choice: %s' % (str))
    return str

def AskIfIdentify(c):
    print '%s' % (repo.commit(c).message )
    print '------------------------------------------'
    print 'Author: %s [%s]' % (repo.commit(c).author.name, str(repo.commit(c).author.email))
    print '------------------------------------------'
    return AskyN('Enter mark or press Enter to skip ?')

def AskIfSplit(flist):
    print('Modified %d files' % (len(flist)))
    for f in flist:
       print('    %s' % (f))
    return AskyN('Split Commit ?')

def AskIfReorder(name):
    return AskyN('Reorder domain %s ?' % name)

#
#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
#
def SplitGitCommits(repo, start, end):
    nb_split = 0
    commitlist = []
    cbase_initialized = False

    LogConsoleAndFile('\n')
    LogConsoleAndFile('Split Commits from %s to %s' % (start, end))

    # list commits from A to B
    commitlist = gitGetCommitList(repo, start, end, '.')

    # for each commit ID
    for commit in commitlist:
        filelist = []
        process_commit = True
        split = False

        if cbase_initialized == True:
            repo.git.cherry_pick(commit, '--ff') # cherry-pick commit
            src_cobj = repo.head.commit
        else:
            src_cobj = repo.commit(commit)

        if IsMarked(src_cobj.summary):
            LogCpGeneric('[X]', commit, src_cobj.hexsha,src_cobj.summary, filelist)
            continue

        filelist = GetFlistFromCommit(repo, src_cobj.hexsha) # list files modified

        while process_commit == True:
            flist_staged =  []
            dlist = []

            if len(filelist) == 0 : #Stop if no files
                process_commit = False
                break

            dlist = GetDomainsFromFlist(filelist)
            if len(dlist) == 0 or (len(dlist)==1 and dlist[0]['path'] == 'unknown'): # no domain identified
                domain = unknown_domain
                if split != True: # if not part of a split, go to next
                    LogCpGeneric('[ ]', commit, src_cobj.hexsha, src_cobj.summary, filelist)
                    break
                else: # part of a split commit
                    flist_staged = FilterInDomain(filelist, domain['path'])

            elif len(dlist) == 1 and dlist[0]['path'] != 'unknown': # only one domain identified.
                domain = dlist[0]
                flist_staged = FilterInDomain(filelist, domain['path'])
                if split != True: # if not part of a split, go to next
                    LogCpGeneric('[ ]', commit, src_cobj.hexsha, src_cobj.summary, filelist)
                    break # if not part of a split, go to next

            else: # several domain identified
                domain = dlist[0]
                flist_staged = FilterInDomain(filelist, domain['path'])

            logging.debug('------------filelist------------------')
            for f in  filelist:
                logging.debug('   %s' % f)
            logging.debug('------------staged--------------------')
            for f in  flist_staged:
                logging.debug('   %s' % f)
            logging.debug('--------------------------------------')


            if split != True:
                if len(filelist) == len(flist_staged):
                    process_commit = False
                    LogCpGeneric('[*]', commit, src_cobj.hexsha, src_cobj.summary, filelist, dlist)
                    break
                else : # if this commit requires split

                    if getDomListOption(dlist, "no-split") == True: # if marked as no-split
                        LogCpGeneric('[U]', commit, src_cobj.hexsha, src_cobj.summary, filelist, dlist)
                        break

                    if interactive == True:
                        if AskIfSplit(filelist) == False: # if user rejected split
                            # Then do not split
                            process_commit = False
                            LogCpGeneric('[ ]', commit, src_cobj.hexsha, src_cobj.summary, filelist, dlist)
                            break

                    if cbase_initialized == False:
                        # initialize source when 1st change in history happens
                        repo.git.checkout(commit, '-f')
                        src_cobj = repo.head.commit
                        cbase_initialized = True

                    LogSplit(commit, src_cobj.summary, filelist)
                    os.system('git reset -q HEAD~')
                    #sys.exit(0)
                #endif

            if cbase_initialized == False:
                # initialize source when 1st change in history happens
                repo.git.checkout(commit, '-f')
                src_cobj = repo.head.commit
                cbase_initialized = True

            for f in flist_staged:
                filelist.remove(f)

            dpath = domain['path']
            dmsg = domain['msg']

            for f in flist_staged:
                #logging.debug('git add -A %s' % f)
                os.system('git add -A ' + f)

            # commit
            os.system('git commit -q -C ' + commit)

            if len(filelist) != 0 : # if some files remains uncommitted
                split = True
            else:
                process_commit = False

            if split == True: #if current commit is a part of a split
                if src_cobj.message.startswith(dmsg) == True:
                    message = '[SPLIT] ' + src_cobj.message
                else:
                    message = '[SPLIT] ' + dmsg + ' ' + src_cobj.message
                gitAmendMsg(repo, message)
                LogSplitResult(repo, commit, dpath, flist_staged, filelist)

        #end while

    #end for
    if cbase_initialized == False:
        # initialize source when 1st change in history happens
        repo.git.checkout(end, '-f')
    nb_split = len(gitGetCommitList(repo, start, repo.head.commit.hexsha, '.')) - len(commitlist)
    return nb_split


#
#------------------------------------------------------------------------------
# Print Help
#------------------------------------------------------------------------------
#
def LogHelp():
    print 'GitSplit.py --start <commitid> --end <commitid>'
    print ''
    print '     --range       : whole commit range'
    print '-i   --interactive : interactive mode'
    print '     --json        : specify json file'
    print ''
    print 'Example:'
    print '     $ GitSplit.py --range HEAD~15..HEAD'
    print ''

    print ' [ ]: Straigth cherry-pick'
    print ' [-]: Straigth cherry-pick of an undefined domain'
    print ' [U]: Unsplit'
    print ' [E]: Generic error'
    print ' [X]: Excluded'
    print ' [C]: Conflict'


###############################################################################
#
# Main
#
###############################################################################


rev_a = ''
rev_b = ''
range_work = []

verbose=False
interactive = False
do_splitclean = False

# enable logging
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)

# Get options
try:
   opts, args = getopt.getopt(sys.argv[1:],"hiv",["interactive","verbose","exclude=","range=","json"])
except getopt.GetoptError:
   LogHelp()
   sys.exit(0)

for opt, arg in opts:
    if opt == '-h':
        LogHelp()
        sys.exit()
    elif opt in ("-i", "--interactive"):
        interactive = True
    elif opt in ("-v", "--verbose"):
        verbose = True
    elif opt in ("-j", "--json"):
        json_file = arg
    elif opt in ("-r", "--range"):
        range_work = arg
    else:
        print 'Unknown option %s' % opt
        LogHelp()

#------------------------------------------------------------------------------
# Sanity checks
#------------------------------------------------------------------------------
if len(range_work) == 0:
    print 'WARNING: missing range parameter'
    sys.exit(0)

repo = git.Repo(".")
CheckRepoIsClean()

#------------------------------------------------------------------------------
# Json
#------------------------------------------------------------------------------
if os.path.isfile(json_file) == False:
    print 'ERROR: Json resource file %s does not exist' % json_file
    sys.exit(2)

with open(json_file) as data_file:
    json_data = json.loads(data_file.read())

json_marklist = json_data["marklist"]
json_domainlist = json_data["domainlist"]
json_domainwildcard = json_data["domainwildcard"]

for d in json_domainlist:
    if d['path'].startswith('unknown') == True:
        unknown_domain = d

#------------------------------------------------------------------------------
# Proceed
#------------------------------------------------------------------------------

# init head commits
rev_a, rev_b = RangeParse(range_work)
new_top = head_split = head_reorder = rev_b

nb_split = SplitGitCommits(repo, rev_a, rev_b)
head_split = repo.head.commit.hexsha
new_top = repo.head.commit.hexsha


#------------------------------------------------------------------------------
# Report
#------------------------------------------------------------------------------
LogConsoleAndFile('')
if repo.head.commit.hexsha != repo.commit(rev_b).hexsha:
    LogConsoleAndFile('git diff --name-status %s..%s' % (rev_b, head_reorder))
    os.system('git diff --name-status %s..%s' % (rev_b,head_reorder))
else:
    LogConsoleAndFile(' No Changes')

LogConsoleAndFile('')
LogCommitRange('Base range :', rev_a, rev_b)
LogCommitRange('Split range:', rev_a, Sid(head_split))
LogConsoleAndFile('')
LogConsoleAndFile('Split %d commits' % nb_split)

