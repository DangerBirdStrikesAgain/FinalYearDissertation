import matplotlib.pyplot as plt
import numpy as np
import matplotlib

"""
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'sans-serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})
"""

covFloor = [10.91, 1.75, 0.44, 0.11, 0.02]
meanTime=[0.1, 12.8, 153.0, 618.9, 44829.7]

xbase = np.linspace(0.00000001,11,1000)
ybase = (1/xbase**2)

plt.plot(xbase, ybase, color="black")


for x in range (0, len(covFloor)):
    plt.plot(covFloor[x], meanTime[x],  marker="o", color="blue")
plt.plot(1.13,69.287, marker="o", color="cyan")

plt.xlim(0, 11)
plt.ylim(0, 44829)



plt.xlabel("Coverage floor /%")
plt.ylabel("Average latency /Seconds")

plt.show()
#plt.savefig('distanceIntervals.pgf')