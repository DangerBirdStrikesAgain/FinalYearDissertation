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

B1a = pandas.read_csv('B1a.csv')
# Only have ones about messages i.e. logging event number 3
B1a = B1a[B1a['3']==3]
timeTotal = timeDifference(B1a['1'].iloc[-1], B1a['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B1a.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B1a.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")




B1b = pandas.read_csv('B1b.csv')
# Only have ones about messages i.e. logging event number 3
B1b = B1b[B1b['3']==3]
timeTotal = timeDifference(B1b['1'].iloc[-1], B1b['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B1b.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B1b.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")



B1c = pandas.read_csv('B1c.csv')
# Only have ones about messages i.e. logging event number 3
B1c = B1c[B1c['3']==3]
timeTotal = timeDifference(B1c['1'].iloc[-1], B1c['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B1c.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B1c.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")



B2a = pandas.read_csv('B2a.csv')
# Only have ones about messages i.e. logging event number 3
B2a = B2a[B2a['3']==3]
timeTotal = timeDifference(B2a['1'].iloc[-1], B2a['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B2a.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B2a.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")



B2b = pandas.read_csv('B2b.csv')
# Only have ones about messages i.e. logging event number 3
B2b = B2b[B2b['3']==3]
timeTotal = timeDifference(B2b['1'].iloc[-1], B2b['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B2b.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B2b.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")



B2c = pandas.read_csv('B2c.csv')
# Only have ones about messages i.e. logging event number 3
B2c = B2c[B2c['3']==3]
timeTotal = timeDifference(B2c['1'].iloc[-1], B2c['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B2c.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B2c.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")


B4a = pandas.read_csv('B4a.csv')
# Only have ones about messages i.e. logging event number 3
B4a = B4a[B4a['3']==3]
timeTotal = timeDifference(B4a['1'].iloc[-1], B4a['1'].iloc[0])
# Calculate the total number of messages transferred 
# Get rid of anything that isn't messages
B4a.drop(['0', '1', '2', '3'], axis=1,  inplace=True)
msgs = []
for label, content in B4a.items():
    for item in content:
        if not (item in msgs) and not (item != item):
            msgs.append(item)
print(f"Bandwidth is {len(msgs)/timeTotal} per second")





