"""
Extract results of the five node field test
"""

import pandas
import math

def timeDifference(time1, time2):
    """
    Calculates the number of seconds between two times
    time2 is the smaller time 
    time format hh.mm.ss -- assumes on same day 
    """
    t1 = str(time1).split(".")
    t2 = str(time2).split(".")

    t1 = int(t1[0])*60*60 + int(t1[1])*60 + int(t1[2])
    t2 = int(t2[0])*60*60 + int(t2[1])*60 + int(t2[2])

    return t1-t2 


def getSeconds(time):
    t1 = str(time).split(".")
    t1 = int(t1[0])*60*60 + int(t1[1])*60 + int(t1[2])
    return t1


def smallest(times):
    """
    Finds the smallest time and therefore generating node from a list
    """
    t = str(times[0]).split(".")
    currentSmallest = int(t[0])*60*60 + int(t[1])*60 + int(t[2])
    lst = []
    lst.append(currentSmallest)

    for x in times: 
        i = str(x).split(".")
        tmp = int(i[0])*60*60 + int(i[1])*60 + int(i[2])
        if tmp<currentSmallest:
            currentSmallest = tmp
        lst.append(tmp) 
    lst.append(currentSmallest)    
    return lst


def tiny(times):
    """
    Finds the smallest time and therefore generating node from a list
    """
    t = str(times[0]).split(".")
    currentSmallest = int(t[0])*60*60 + int(t[1])*60 + int(t[2])

    for x in times: 
        i = str(x).split(".")
        tmp = int(i[0])*60*60 + int(i[1])*60 + int(i[2])
        if tmp<currentSmallest:
            currentSmallest = tmp
    return currentSmallest



a = pandas.read_csv('a.csv') 
b = pandas.read_csv('b.csv')
c = pandas.read_csv('c.csv') 
d = pandas.read_csv('d.csv') 
e = pandas.read_csv('e.csv') 

# Only have ones about messages i.e. logging event number 3
a = a[a['3']==3]
b = b[b['3']==3]
c = c[c['3']==3]
d = d[d['3']==3]

# Drop anything that isn't a timestamp or a message
a.drop(['0', '2', '3'], axis=1,  inplace=True)
b.drop(['0', '2', '3'], axis=1,  inplace=True)
c.drop(['0', '2', '3'], axis=1,  inplace=True)
d.drop(['0', '2', '3'], axis=1,  inplace=True)

# Okay so find the time when things were generated the last time they arrive
aTimes = {}
for i in range(0, len(a)-1):
    row = a.iloc[i]
    for x in range(1, 77):
        temp = row.iloc[x]
        try:
            if math.isnan(temp):
                break
        except:
            pass
        if temp not in aTimes.keys():
            aTimes.update({temp : row.iloc[0]})

bTimes = {}
for i in range(0, len(b)-1):
    row = b.iloc[i]
    for x in range(1, 77):
        temp = row.iloc[x]
        try:
            if math.isnan(temp):
                break
        except:
            pass
        if temp not in bTimes.keys():
            bTimes.update({temp : row.iloc[0]})

cTimes = {}
for i in range(0, len(c)-1):
    row = c.iloc[i]
    for x in range(1, 77):
        temp = row.iloc[x]
        try:
            if math.isnan(temp):
                break
        except:
            pass
        if temp not in cTimes.keys():
            cTimes.update({temp : row.iloc[0]})

dTimes = {}
for i in range(0, len(d)-1):
    row = d.iloc[i]
    for x in range(1, 77):
        temp = row.iloc[x]
        try:
            if math.isnan(temp):
                break
        except:
            pass
        if temp not in dTimes.keys():
            dTimes.update({temp : row.iloc[0]})

all = {}
average = []
for item in aTimes.keys():
    # get lowest and highest latency times here
    temp = []
    temp.append(aTimes[item])
    if item in bTimes.keys():
        temp.append(bTimes[item])
    if item in cTimes.keys():
        temp.append(cTimes[item])
    if item in dTimes.keys():
        temp.append(dTimes[item])
    if len(temp)>1:
        all.update({item:temp})

# now you should have a dictionary of each message id and the four times


# find the generating node (smallest time)
"""
for item in all.keys():
    tmp = all[item]
    small = smallest(tmp)
    all.update({item: small})

for item in all.keys():
    times = all[item]
    for x in range (0, len(times)-1):
        average.append(times[x]-times[-1])

while 0 in average:
    average.remove(0)

print(sum(average)/(len(average)))
print(max(average))
        
"""
"""

for item in all.keys():
    tmp = all[item]
    tin = tiny(tmp)
    all.update({item: tin})
# find the latencies of all packet deliveries
# find the average latency 

aList = []
for item in aTimes.keys():
    if item in all:
        aList.append(getSeconds(aTimes[item])-all[item])

while 0 in aList:
    aList.remove(0)

bList = []
for item in bTimes.keys():
    if item in all:
        bList.append(getSeconds(bTimes[item])-all[item])

while 0 in bList:
    bList.remove(0)

cList = []
for item in cTimes.keys():
    if item in all:
        cList.append(getSeconds(cTimes[item])-all[item])

while 0 in cList:
    cList.remove(0)


dList = []
for item in dTimes.keys():
    if item in all:
        dList.append(getSeconds(dTimes[item])-all[item])

while 0 in dList:
    dList.remove(0)

print(f"a = {aList}")
print(f"b = {bList}")
print(f"c = {cList}")
print(f"d = {dList}")
"""



for item in all.keys():
    tmp = all[item]
    small = smallest(tmp)
    all.update({item: small})

for item in all.keys():
    times = all[item]
    tmp = []
    for x in range (0, len(times)-1):
        t = times[x]-times[-1]
        if t!=0:
            tmp.append(t)
    average.append(sum(tmp)/len(tmp))

while 0 in average:
    average.remove(0)

print(sum(average)/len(average))
print(average)