import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'sans-serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})

results0 = [0, 6, 30, 3, 11, 6, 6, 45, 44, 36, 74, 33, 32, 22, 19, 57, 10, 7, 7, 7, 40, 6, 6, 12, 9, 26, 24, 24, 13, 9, 27, 27, 26, 14, 14, 9, 3, 9, 9, 9, 19, 14, 8, 5, 16, 14, 13, 13, 5, 7, 6, 4, 8, 8, 4, 8, 6, 5, 8, 3, 12, 4, 5, 14, 5, 4, 4]
results10 = [0, 5, 6, 6, 3, 10, 8, 8, 8, 7, 3, 3, 3, 7, 4, 4, 5, 6, 6, 6, 36, 30, 27, 17, 8, 6, 19, 19, 18, 17, 10, 21, 20, 15, 14, 5, 4, 4, 5,  27, 27, 27, 25, 24, 21, 92, 19, 15, 13, 84, 46, 9, 9, 14,  11, 7, 6, 7, 44, 8, 8, 18, 16, 14, 11]
results100 = [0, 76, 58, 23, 21, 21, 14, 10, 39, 6, 6, 59, 6, 6, 22, 22, 15, 13, 13, 12, 10, 9, 21, 12, 12, 12, 52, 22, 14, 137, 135, 135, 128, 119, 117, 105, 103, 103, 5, 2, 22, 22, 22, 15, 78, 8, 71, 10, 9, 14, 14, 73, 6, 15, 15, 15, 13, 7, 57, 7, 50, 48, 47, 32, 27, 20, 11, 4, 4, 7, 6]
results250 = [0, 303, 78, 39, 333, 12, 47, 117, 18, 210, 58, 73, 333, 16, 34, 165, 45, 371, 168, 399, 36, 18, 360, 45, 110, 111, 358, 284, 320, 65, 20, 186, 71, 301, 395, 31, 82, 340, 101, 288, 115, 240, 217, 48, 245, 59, 37, 26, 18, 24, 24, 48, 43, 73, 218, 98, 270, 360, 297]
results500 = [0, 249, 385, 313, 267, 32, 69, 295, 342, 302, 56, 27, 29, 338, 65, 208, 45, 455, 487, 139, 66, 49, 95, 211, 117, 163, 154, 327, 300, 23, 477, 206, 134, 46, 31, 309, 20, 379, 299, 421, 298, 326, 258, 342, 338, 284, 340, 348, 150, 210, 267, 385, 494, 436, 169, 332, 161]


results0.sort()
results10.sort()
results100.sort()
results250.sort()
results500.sort()

per0=[0]
per10=[0]
per100=[0]
per250=[0]
per500=[0]

temp = 100/(len(results0)-1)
for x in range(1, len(results0)):
    per0.append(temp*x)

temp = 100/(len(results10)-1)
for x in range(1, len(results10)):
    per10.append(temp*x)


temp = 100/(len(results100)-1)
for x in range(1, len(results100)):
    per100.append(temp*x)


temp = 100/(len(results250)-1)
for x in range(1, len(results250)):
    per250.append(temp*x)

temp = 100/(len(results500)-1)
for x in range(1, len(results500)):
    per500.append(temp*x)

plt.xlim(0, 510)
plt.ylim(0, 100)
plt.grid()

"""
plt.plot(results0, per0, color="blue", label='0m',  marker='.')
plt.plot(results10, per10, color="red", label='10m', marker='+')
plt.plot(results100, per100, color="green", label='100m', marker='d')
plt.plot(results250, per250, color="cyan", label='250m', marker='*')
plt.plot(results500, per500, color="magenta", label='500m', marker='s')
"""

plt.plot(results0, per0, color="blue", label='0m')
plt.plot(results10, per10, color="red", label='10m')
plt.plot(results100, per100, color="green", label='100m')
plt.plot(results250, per250, color="cyan", label='250m')
plt.plot(results500, per500, color="magenta", label='500m')


plt.legend(loc='lower right')
plt.xlabel("Time taken /Seconds")
plt.ylabel("Percentage of packets delivered")

plt.savefig('percentages.pgf')
