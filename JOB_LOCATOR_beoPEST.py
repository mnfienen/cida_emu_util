import re
import os
import numpy as np
from JOB_LOCATOR_UTILITIES import parse_job_file, logfail,cqrfail

rmr_file       = 'testing.rmr'
user_name      = 'rjhunt-pr'
IP_lookup_file = 'name_IP_lookup.dat'
cluster_num    = 250

class PESTnum:
    def __init__(self,pestnum,runloc):
        self.runloc = runloc
        self.pestnum = pestnum
        runlocsplit = runloc.split('\\')
        self.runIP = runloc.split('\\')[0]
        for i in runlocsplit:
            if 'dir_' in i.lower():
                self.rundir = i.lower()

class CONDORnum:
    def __init__(self,condornum,condorslot):
        self.condornum = condornum
        self.condorslot = condorslot.split('@')[0]
        self.condormachine = condorslot.split('@')[1]
        self.condormachname = self.condormachine.split('.')[0]
        
        
# ### Read in and parse the IP lookup file
indat = np.genfromtxt(IP_lookup_file,dtype=None,names=True)
IPlookup = dict(zip(indat['comp_name'],indat['IP_address']))
NAMElookup = dict(zip(indat['IP_address'],indat['comp_name']))
del indat

# ### PARSE condor_q -run Results to link slots with jobs
#os.system('condor_q -run > cqr')


cqout = open('cqr','r').readlines()
#os.remove(os.path.join(os.getcwd(),'cqr'))
CONDORruns = []
for line in cqout:
    tmp = line.lower().strip().split()
    if user_name.lower() in line:
        CONDORruns.append(CONDORnum(tmp[0],tmp[-1]))

# ### Parse the RMR file to link PEST_jobs with locations
indat = open(rmr_file,'r').readlines()
PESTruns = []
for line in indat:
    if 'assigned to node at working directory' in line:
        PESTjobs = re.findall("index of (.*?) assigned to node at working",line)
        FolderLocations = line.strip().split()[-1][1:-2]
        PESTruns.append(PESTnum(PESTjobs[0],FolderLocations))
        
        
# ### Go through the Condor jobs and find the run directories for each Condor job
for crun in CONDORruns:
    ccluster = crun.condornum.split('.')[0]
    if int(ccluster) == cluster_num:
        currip,curd = parse_job_file(int(ccluster),crun.condornum.split('.')[1])
        jj = curd.split('\\')
        for i in jj:
            if 'dir_' in i.lower():
                crun.rundir = i.lower()
#depracated                if crun.condornum != lognum[0]:
#depracated                    raise(logfail(lognum[0],crun.condornum,crun.condormachname,crun.condorslot))
            
# ### prepare an output file
ofp = open(rmr_file[:-4] + '_jobs_machines.dat','w')
ofp.write('%9s%12s%20s%17s%16s%10s\n' %('PestNode','CondorRun','MachineName','IPAddress','RunDir','Slot'))
            
# ### NOW DO ALL THE MATCHMAKING
for cp in PESTruns:
    ofp.write('%9s' %(cp.pestnum))
    for cc in CONDORruns:
        if NAMElookup[cp.runIP] in cc.condormachine.lower():
            if cp.rundir == cc.rundir:
                ofp.write('%12s' %(cc.condornum))
                ofp.write('%20s' %(cc.condormachname))
                ofp.write('%17s' %(cp.runIP))
                ofp.write('%16s' %(cc.rundir))
                ofp.write('%10s\n' %(cc.condorslot))
ofp.close()
                
    
i=1
