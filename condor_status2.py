import os

os.system('condor_status -l > cslog')

indat = open('cslog','r').readlines()

Machine = []
Name = []
OpSys = []
Arch = []
State = []
Activity = []
LoadAvg = []
Mem = []


# Parse the condor_status -l results

for line in indat:
    if line.split(' =')[0] == 'Machine':
        tmp = (line.split('"')[1])
        Machine.append(tmp.split('.')[0])
    elif line.split(' =')[0] == 'OpSys':
        OpSys.append(line.split('"')[1])
    elif line.split(' =')[0] == 'Name':
        tmp = (line.split('"')[1])
        Name.append(tmp.split('.')[0])
    elif line.split(' =')[0] == 'Arch':
        Arch.append(line.split('"')[1])
    elif line.split(' =')[0] == 'State':
        State.append(line.split('"')[1])
    elif line.split(' =')[0] == 'Activity':
        Activity.append(line.split('"')[1])
    elif line.split(' =')[0] == 'LoadAvg':
        LoadAvg.append(line.strip().split('=')[1])
    elif line.split(' =')[0] == 'Memory':
        Mem.append(line.strip().split('=')[1])

# now print them out the the screen
outfmt = '%23s%10s%8s%10s%7s%8s'  
print outfmt %('Name','OpSys','Arch','State','Activity','Mem')
for i in range(len(Name)):
    print outfmt %(Name[i],OpSys[i], Arch[i], State[i], Activity[i], Mem[i])
os.remove('cslog')