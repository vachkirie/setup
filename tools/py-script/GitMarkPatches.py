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


log_file = '.GitMarkPatches.log'
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
    log=[]
    output=''

    for i in tab:
        if (i[0] == base) and (i[1] == top):
            found = True
            log = i[2]

    cmd = 'git log --pretty=format:"%h %s" '+base+'..'+top

    if found == False:
        output = ShellCmd(cmd)
        output = output.split("\n")
        for l in output:
            log.append(l.split(' ',1))

    if found == False:
        tab.append([base, top, log])
        logging.info(('tab new entry %d [%s, %s]' % (len(tab), base, top)))

    return log


def FindSummaryInLog(repo, base, top, sum):
    log = GitLogSummary(repo, base, top)

    sum = repr(sum)
    if len(log)>1:
        for i in log:
            if repr(i[1]) == sum: return True
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
    if path != '.':
        path = path + '*'
    text = repo.git.rev_list('%s..%s' % (a,b), path).split("\n")
    commitIDs.extend(text)

    logging.debug('gitGetCommitList: git rev-list %s..%s %s' % (a,b,path))
    for commit in commitIDs:
        logging.debug('gitGetCommitList:   %s - %s' % (Sid(commit), repo.commit(commit).summary))

    commitIDs.reverse()

    if path == '.':
        return commitIDs

    if len(commitIDs) < 10: # invalid sha list
        logging.debug('gitGetCommitList: %d - %s' % (len(commitIDs), commitIDs))
        return clist_strip

    for c in commitIDs:
        dlist = GetDomainsFromCommit(repo, c)
        cpath = dlist[0]
        if cpath != None:
            path = path.replace('*','')
            if cpath['path'] == path:
                clist_strip.append(c)
                logging.debug('gitGetCommitList:     keep %s from %s' % (Sid(c),path))
            else:
                logging.debug('gitGetCommitList:     discard %s from %s (%s)' % (Sid(c),path,cpath['path']))
        else:
            logging.debug('gitGetCommitList:     discard %s from %s (None)' % (Sid(c),path))

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
    # look for a domain by excluding wildcard files
    for f in flist:
        if FileIsWildcard(f) == True:
            continue

        domain = getFileDomain(f)
        if domain == None:
            domain = unknown_domain
            flist_unknown.append(f)

        logging.debug('GetDomainsFromFlist: %s from %s' % (f, domain['path']))
        if domain not in dlist:
            dlist.append(domain)

    # look for a domain including wildcard files
    if len(dlist) == 0 and len(flist) > 0:
        for f in flist:
            domain = getFileDomain(f)
            if domain == None:
                if FileIsWildcard(f) == True:
                    continue
                domain = unknown_domain
                flist_unknown.append(f)

            logging.debug('GetDomainsFromFlist: %s from %s' % (f, domain['path']))
            if domain not in dlist:
                dlist.append(domain)


    if len(dlist) == 0 and len(flist) > 0:
        dlist.append(unknown_domain)

    dlist.reverse()
    # move unknown domain to end of list
    if unknown_domain in dlist:
        dlist.remove(unknown_domain)
        dlist.append(unknown_domain)

    #LogConsoleAndFile('GetDomainsFromFlist %s' % dlist)
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


def Strip_SlogList(la, lb):
    slist_res = copy.deepcopy(la)

    for i in lb:
        torm=[]
        sum = RemoveMark(i[1])
        for j in slist_res:
            if sum == j[1]:
                torm = j
                break
        if len(torm) > 0 :
            slist_res.remove(torm)
    return slist_res

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


def RangeParse(s):
    if len(s) == 0:
        return None, None

    temp = s.replace(".."," ").split()
    return temp[0], temp[1]



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

def GetGoogleMark():
    for m in json_marklist:
        for sm in m:
            if sm['mark'].startswith('[GOOGLE'): return sm
    sys.exit(2)
    return None

def IsMarked(s):
    if s.startswith('[EXTERNAL] '):
        return True

    for m in json_marklist:
        for sm in m:
            if s.startswith(sm['mark']): return True
    return False


def RemoveMark(s):
    s = s.replace('[EXTERNAL] ','')
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

    if len(version) == 0: #if no version identified
        if '@intel.com' in repo.commit(c).author.email: # if from sofia internal developer
            return version
        else: # then it is external unidentified
            version = '[EXTERNAL] '

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

def GitMarkAddCommit2version(list, version):
    found = False
    for i in list:
        if i[0] == version:
            i[1] = i[1]+1
            found = True

    if found == False:
        clist_marked.append([version, 1])


#------------------------------------------------------------------------------
# Proceed
#------------------------------------------------------------------------------
def GitMarkPatches(cbase, ctop):
    cbase_initialized = False
    clist = []
    clist_marked = []
    nb_marked = 0

    # list commits from A to B
    clist = gitGetCommitList(repo, cbase, ctop, '.')
    if len(clist) == 0:
        print 'ERROR: empty range %s..%s' % (cbase,ctop)
        sys.exit(0)

    LogConsoleAndFile('\n')
    LogConsoleAndFile('Processing commits from %s..%s' % (cbase, ctop))

    # for each commit ID
    for c in clist:
        src_cobj = repo.commit(c)
        new_cobj = src_cobj

        if dry_run == False and cbase_initialized == True:
            repo.git.cherry_pick(c, '--ff') # cherry-pick commit
            new_cobj = repo.head.commit

        version = GetMarkVersion(repo, c)
        if len(version) == 0: #if no version identified
            LogConsoleAndFile('[ ] %s --> %s - %s' % (Sid(src_cobj.hexsha), Sid(new_cobj.hexsha), new_cobj.summary))
            continue
        elif version == '[EXTERNAL] ': # then it is external unidentified
            logging.info('------------------------------------------')
            logging.info('Author: %s [%s]' % (src_cobj.author.name, str(src_cobj.author.email)) )
            logging.info('------------------------------------------')

        if IsMarkedRight(version, src_cobj.summary): # if yet marked with correct version
            LogConsoleAndFile('[-] %s --> %s - %s' % (Sid(src_cobj.hexsha), Sid(new_cobj.hexsha), new_cobj.summary))
            GitMarkAddCommit2version(clist_marked, version)
            continue


        if dry_run == False and cbase_initialized == False:
            # initialize source when 1st change in history happens
            repo.git.checkout(c, '-f')
            cbase_initialized = True

        message = RemoveMark(new_cobj.message)  # clean mark if any
        message = "%s%s" % (version, str(message.encode('utf-8')))
        summary = RemoveMark(new_cobj.summary)  # clean mark if any
        summary = "%s%s" % (version, str(summary.encode('utf-8')))

        if dry_run == False:
            # Amend commit message
            FileWrite('fmsg', message)
            os.system('git commit --amend --quiet -F fmsg')
            new_cobj = repo.head.commit

        nb_marked +=1 # count modified commits

        LogConsoleAndFile('[M] %s --> %s - %s' % (Sid(src_cobj.hexsha), Sid(new_cobj.hexsha), summary))
        GitMarkAddCommit2version(clist_marked, version)

    #end for
    if cbase_initialized == False:
        # initialize source when 1st change in history happens
        repo.git.checkout(ctop, '-f')

    return clist, clist_marked, nb_marked

def GitUnMarkPatches(cbase, ctop):
    cbase_initialized = False
    clist = []
    clist_marked = []
    nb_marked = 0

    # list commits from A to B
    clist = gitGetCommitList(repo, cbase, ctop, '.')
    if len(clist) == 0:
        print 'ERROR: empty range %s..%s' % (cbase,ctop)
        sys.exit(0)

    LogConsoleAndFile('\n')
    LogConsoleAndFile('Processing commits from %s..%s' % (cbase, ctop))

    # for each commit ID
    for c in clist:
        src_cobj = repo.commit(c)
        new_cobj = src_cobj

        if dry_run == False and cbase_initialized == True:
            repo.git.cherry_pick(c, '--ff') # cherry-pick commit
            new_cobj = repo.head.commit

        if not IsMarked(src_cobj.summary): # if yet marked with correct version
            LogConsoleAndFile('[ ] %s --> %s - %s' % (Sid(src_cobj.hexsha), Sid(new_cobj.hexsha), new_cobj.summary))
            continue

        if dry_run == False and cbase_initialized == False:
            # initialize source when 1st change in history happens
            repo.git.checkout(c, '-f')
            cbase_initialized = True

        message = RemoveMark(new_cobj.message)  # clean mark if any
        message = "%s" % (str(message.encode('utf-8')))
        summary = RemoveMark(new_cobj.summary)  # clean mark if any
        summary = "%s" % (str(summary.encode('utf-8')))

        if dry_run == False:
            # Amend commit message
            FileWrite('fmsg', message)
            os.system('git commit --amend --quiet -F fmsg')
            new_cobj = repo.head.commit

        nb_marked +=1 # count modified commits

        LogConsoleAndFile('[M] %s --> %s - %s' % (Sid(src_cobj.hexsha), Sid(new_cobj.hexsha), summary))

    #end for
    if cbase_initialized == False:
        # initialize source when 1st change in history happens
        repo.git.checkout(ctop, '-f')

    return clist, clist_marked, nb_marked



#
#------------------------------------------------------------------------------
# Print Help
#------------------------------------------------------------------------------
#
def LogHelp():
    print 'GitMarkPatches.py --range <id>..<id> [--dry-run, --interactive] '
    print ''
    print '     --range       : whole commit range'
    print '-i   --interactive : interactive mode'
    print '     --json        : specify json file'
    print '-n   --dry-run     : no changes made to history'
    print ''
    print 'Example:'
    print '     $ GitMarkPatches.py --range HEAD~15..HEAD~10'
    print ''

    print ' [ ]: from internal developer'
    print ' [-]: external yet marked'
    print ' [M]: external newly marked'


###############################################################################
#
# Main
#
###############################################################################
range_work = ''

dry_run = False
verbose=False
interactive = False
check_google = False
unmark = False

# enable logging
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)

# Get options
try:
    opts, args = getopt.getopt(sys.argv[1:],"hivj:rng:u",["interactive","verbose","json=","range=", "dry-run","google","unmark"])
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
        logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG)
        verbose = True
    elif opt in ("-j", "--json"):
        json_file = arg
    elif opt in ("-r", "--range"):
        range_work = arg
    elif opt in ("-n", "--dry-run"):
        dry_run = True
    elif opt in ("-g", "--google"):
        check_google = True
    elif opt in ("-u", "--unmark"):
        unmark = True
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
cbase = ''
ctop = ''
clist = []
clist_marked = []
nb_marked = 0

# init head commits
cbase, ctop = RangeParse(range_work)
if unmark == True:
    clist, clist_marked, nb_marked = GitUnMarkPatches(cbase, ctop)
else:
    clist, clist_marked, nb_marked = GitMarkPatches(cbase, ctop)

#------------------------------------------------------------------------------
# Check Google patch list
#------------------------------------------------------------------------------
LogConsoleAndFile('')
GMark = GetGoogleMark()
LogConsoleAndFile('Checking Google patch list: %s in %s..%s' % (GMark['mark'], GMark['base'], GMark['top']))
slist_current = GitLogSummary(repo, GMark['base'], repo.head.commit.hexsha)
slist_google = GitLogSummary(repo, GMark['base'], GMark['top'])
slist_missing = Strip_SlogList(slist_google, slist_current)

for i in slist_missing:
    logging.info('   %s - %s' % (i[0],i[1]))
    if check_google == True:
        print'   %s - %s' % (i[0],i[1])

LogConsoleAndFile('')
LogConsoleAndFile('Missing: %d/%d patches from(%s..%s)' % (len(slist_missing),len(slist_google),GMark['base'], GMark['top']))

#------------------------------------------------------------------------------
# Report
#------------------------------------------------------------------------------
total = 0
LogConsoleAndFile('')
if repo.head.commit.hexsha != repo.commit(ctop).hexsha:
    LogConsoleAndFile('git diff --name-status %s..%s' % (ctop, repo.head.commit.hexsha))
    os.system('git diff --name-status %s..%s' % (ctop,repo.head.commit.hexsha))
else:
    LogConsoleAndFile(' No Changes')

LogConsoleAndFile('')
LogConsoleAndFile('Initial range: %s..%s' % (cbase, ctop))
LogConsoleAndFile('Final range:   %s..%s' % (cbase, Sid(repo.head.commit.hexsha)))


LogConsoleAndFile('')
for i in clist_marked:
        count = i[1]
        if count > 0:
            LogConsoleAndFile(' %s%d commits' % (str(i[0]), count))
            total += count

LogConsoleAndFile('')
LogConsoleAndFile('Newly marked %d / %d commits' % (nb_marked,len(clist)))
LogConsoleAndFile('Marked %d / %d commits' % (total,len(clist)))

