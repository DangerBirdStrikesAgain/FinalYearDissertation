"""
Designed to analyze results of the latency testing
This code is awful, I know. I'm tired. 
"""

import pandas
import numpy
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

a = pandas.read_csv('a1.csv')
b = pandas.read_csv('b1.csv')
# Only have ones about messages i.e. logging event number 3
a = a[a['3']==3]
b = b[b['3']==3]

# Drop anything that isn't a timestamp or a message
a.drop(['0', '2', '3'], axis=1,  inplace=True)
b.drop(['0', '2', '3'], axis=1,  inplace=True)


# Okay so find the time when things were generated from a
generated = {}
for i in range(0, len(a)-1):
    row = a.iloc[i]
    for x in range(1, 77):
        temp = row.iloc[x]
        try:
            if math.isnan(temp):
                break
        except:
            pass
        if temp not in generated.keys():
            generated.update({temp : row.iloc[0]})

print(generated)

arrived = {}
for i in range(0, len(b)-1):
    row = b.iloc[i]
    for x in range(1, 77):
        temp = row.iloc[x]
        try:
            if math.isnan(temp):
                break
        except:
            pass
        if temp not in arrived.keys():
            arrived.update({temp : row.iloc[0]})
        

times=[]
for item in generated.keys():
    if item in arrived.keys():
        times.append(timeDifference(arrived[item], generated[item]))

print(times)