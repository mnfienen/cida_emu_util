import re
import os

# ## Parse a process (job) log file
def parse_job_file(clusterno,jobno):
    indat = open(os.path.join(os.getcwd(),'condor_output','w_%d_%d.out' %(int(clusterno),int(jobno))),'r').readlines()
    
    for line in indat:
        if 'ipv4 address' in line.lower():
            currip = line.strip().split()[-1]
            break
        currdir = indat[0]
    return currip,currdir

# ## Parse a slot log file 
def parse_slot_log(indat):
    curr_section = []
    for line in reversed(indat):
        if 'condor_starter (CONDOR_STARTER) STARTING UP' not in line:
            if len(line) > 0:
                curr_section.append(line)
        else:
            break
    del indat
    for line in curr_section:
        if "IWD:" in line:
            curr_wd = line.strip().split()[-1]
        elif "set to execute immediately" in line.lower():
            curr_cond_job = re.findall("Job (.*?) set to execute immediately",line)
    return curr_wd,curr_cond_job
        
# ####################### #
# Error Exception Classes #        
# ####################### #
# -- condor run mismatch
class logfail(Exception):
    def __init__(self,lognum,cqnum,machname,slot):
        self.lognum = lognum
        self.cqnum = cqnum
        self.machname = machname
        self.slot = slot
    def __str__(self):
        return('\n\n Mismatch between condor_q and machine log run numbers.\n' +
               'condor_q says the run is ' + self.cqnum + '\n' + 
               'the machine log for ' + self.slot + ' on ' + self.machname + ' is ' + self.lognum)
        
# -- condor_q failure
class cqrfail(Exception):     
    def __str__():
        return('\n\n Condor_q -run command failed')
        
