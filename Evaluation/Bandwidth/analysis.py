"""
Designed to analyze results of the bandwidth testing
"""

import pandas

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



results = []

B1 = pandas.read_csv('B1.csv')
# Only have ones about messages i.e. logging event number 3
B1 = B1[B1['3']==3]
timeTotal = timeDifference(B1['1'].iloc[-1], B1['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B1.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B1.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)


print(f"Bandwidth is {len(msgs)/timeTotal} per second")
results.append(len(msgs)/timeTotal)



B1p5 = pandas.read_csv('B1p5.csv')
# Only have ones about messages i.e. logging event number 3
B1p5 = B1p5[B1p5['3']==3]
timeTotal = timeDifference(B1p5['1'].iloc[-1], B1p5['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B1p5.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B1p5.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")
results.append(len(msgs)/timeTotal)



B2 = pandas.read_csv('B2.csv')
# Only have ones about messages i.e. logging event number 3
B2 = B2[B2['3']==3]
timeTotal = timeDifference(B2['1'].iloc[-1], B2['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B2.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B2.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")
results.append(len(msgs)/timeTotal)


B2p5 = pandas.read_csv('B2p5.csv')
# Only have ones about messages i.e. logging event number 3
B2p5 = B2p5[B2p5['3']==3]
timeTotal = timeDifference(B2p5['1'].iloc[-1], B2p5['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B2p5.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B2p5.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")
results.append(len(msgs)/timeTotal)


B3 = pandas.read_csv('B3.csv')
# Only have ones about messages i.e. logging event number 3
B3 = B3[B3['3']==3]
timeTotal = timeDifference(B3['1'].iloc[-1], B3['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B3.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B3.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")
results.append(len(msgs)/timeTotal)


B4 = pandas.read_csv('B4.csv')
# Only have ones about messages i.e. logging event number 3
B4 = B4[B4['3']==3]
timeTotal = timeDifference(B4['1'].iloc[-1], B4['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B4.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B4.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")
results.append(len(msgs)/timeTotal)


B5 = pandas.read_csv('B5.csv')
# Only have ones about messages i.e. logging event number 3
B5 = B5[B5['3']==3]
timeTotal = timeDifference(B5['1'].iloc[-1], B5['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B5.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B5.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")
results.append(len(msgs)/timeTotal)



print(results)
