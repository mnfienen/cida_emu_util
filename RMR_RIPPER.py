import re
from datetime import datetime as dt
from datetime import timedelta
import numpy as np
# make a class to hold all model run information
class PESTsum:
    def __init__(self,pestnum,runloc,timestart):
        self.runloc = runloc
        self.pestnum = pestnum
        runlocsplit = runloc.split('\\')
        self.runIP = runloc.split('\\')[0]
        for i in runlocsplit:
            if 'dir_' in i.lower():
                self.rundir = i.lower()
        self.nodestart = timestart
        self.runs = []
        
class arun:
    def __init__(self,node,run,starttime):
        self.pestnum = node
        self.runnum = run
        self.starttime = starttime
        self.endtime = -9999999
        self.elapsed_time = 0
        
        
intimefmt = "%H:%M:%f" # we will ignore the microseconds
  #################################################
 # INSERT THE RMR FILENAME AND UNITS CHOICE BELOW #
##################################################
rmrfile = 'finale21f_reg_svd2.rmr'
timeunits = 'hours' # options are 'minutes','seconds','hours'


IP_lookup_file = 'name_IP_lookup.dat'
timeunits = timeunits.lower()

# ### Read in and parse the IP lookup file
indat = np.genfromtxt(IP_lookup_file,dtype=None,names=True)
IPlookup = dict(zip(indat['comp_name'],indat['IP_address']))
NAMElookup = dict(zip(indat['IP_address'],indat['comp_name']))
del indat

indat = open(rmrfile,'r')

# make a list of nodes - each is a member of class PESTsum
ALLNODES = []
# read the RMR file and populate the PESTsum class members --> also calculate times of all full runs
for line in indat:
    if 'assigned to node at working directory' in line:
        cnode = int(re.findall("index of (.*?) assigned to node at working",line)[0])
        runloc = line.strip().split()[-1][1:-2]
        timestart = line.strip().split('.')[0]
        timestart = dt.strptime(timestart,intimefmt)
        ALLNODES.append(PESTsum(cnode,runloc,timestart))
    elif 'commencing on node' in line:
        crun = int(re.findall("model run (.*?) commencing on node",line)[0])
        sttime = line.strip().split('.')[0]
        cnode = line.strip().split()[-1]
        cnode = int(cnode.split('.')[0])
        sttime = line.strip().split('.')[0]
        sttime = dt.strptime(sttime,intimefmt)
        ALLNODES[cnode-1].runs.append(arun(cnode,crun,sttime))
    elif 'completed on node ' in line:
        crun = int(re.findall("model run (.*?) completed on node",line)[0])
        cnode = line.strip().split()[-1]
        cnode = int(cnode.split('.')[0])
        endtime = line.strip().split('.')[0]
        endtime = dt.strptime(endtime,intimefmt)   
        for current_run in ALLNODES[cnode-1].runs:
            if current_run.runnum == crun:
                current_run.endtime = endtime
                # if the time turns the corner around midnight, assume the end time is in the 
                # next day (NB-->this doesn't account for times longer than 24 hours)
                if current_run.endtime < current_run.starttime:
                    current_run.endtime += timedelta(days=1)
                # calculate the total time in seconds
                current_run.elapsed_time = (current_run.endtime-
                                            current_run.starttime).total_seconds()
del indat

ofp = open(rmrfile + '.RiPpErReD','w')
ofp.write('Rippage of the RMR file called:- ' + rmrfile +'\n')
ofp.write('ALL TIMES REPORTED IN UNITS OF ' + timeunits + '\n')
ofp.write('*==' * 30 + '*\n')
ofp.write('%-8s%-40s%-8s%-12s%-12s%-12s\n' %('Node','Location','NumRuns','meanRunTime','minRunTime','maxRunTime'))

for cnode in ALLNODES:
    rtimes = []
    for crun in cnode.runs:
        if crun.elapsed_time:
            rtimes.append(crun.elapsed_time)
    if len(rtimes)>0:
        rtimes = np.array(rtimes)
        ofp.write('%-8d' %(cnode.pestnum))
        cloc = NAMElookup[cnode.runIP] + '...' + cnode.rundir
        ofp.write('%-40s' %(cloc))
        if timeunits == 'minutes':
            rtimes = rtimes/60.0
        elif timeunits == 'hours':
            rtimes = rtimes/60.0/60.0
        meantimes = np.mean(rtimes)
        mintimes = np.min(rtimes)
        maxtimes = np.max(rtimes)
        ofp.write('%-8d' %(len(rtimes)))
        ofp.write('%-12f' %(meantimes))
        ofp.write('%-12f' %(mintimes))
        ofp.write('%-12f\n' %(maxtimes))
            
ofp.close()

