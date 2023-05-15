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

a = [1, 100, 50, 76, 78, 50, 36, 91, 78, 91, 63, 91, 84, 185, 205, 171, 91, 91, 78, 55, 59, 45, 46, 28, 51, 14, 51, 51, 51, 51, 55, 68, 26, 72, 97, 72, 10, 185]
b = [8, 69, 43, 29, 49, 49, 55, 57, 2, 52, 55, 100, 86, 94, 80, 41, 31, 18, 14, 14, 8, 14, 22, 14, 15, 27, 24, 23, 0, 23, 17, 29, 14, 14, 17, 23, 21, 14, 71, 96]
c = [3, 1, 107, 90, 134, 93, 121, 106, 121, 98, 7, 121, 119, 7, 43, 134, 1, 8, 17, 33, 10, 18, 15, 93, 80, 0, 0, 77, 47, 80, 92, 77, 86]
d = [14, 159, 52, 153, 186, 158, 150, 139, 145, 148, 59, 59, 131, 95, 334, 4, 4, 4, 4, 4, 12, 175, 0, 0, 0, 205, 347]
av = [3.0, 122.0, 101.66666666666667, 68.0, 55.0, 49.75, 49.0, 157.66666666666666, 100.0, 47.666666666666664, 85.0, 92.33333333333333, 46.666666666666664, 69.75, 58.0, 125.5, 92.33333333333333, 82.5, 97.5, 91.0, 73.33333333333333, 154.25, 134.75, 140.25, 62.0, 62.0, 247.0, 60.5, 54.5, 23.0, 21.0, 80.0, 17.0, 48.5, 14.0, 45.5, 14.0, 57.5, 38.75, 37.0, 27.5, 35.666666666666664, 84.5, 30.0, 14.0, 30.0, 32.25, 30.0, 30.0, 34.5, 46.0, 26.0, 54.0, 95.75, 45.75, 10.0, 148.0]
a.sort()
b.sort()
c.sort()
d.sort()
av.sort()

pera=[0]
perb=[0]
perc=[0]
perd=[0]
avper=[0]

temp = 100/(len(a)-1)
for x in range(1, len(a)):
    pera.append(temp*x)

temp = 100/(len(b)-1)
for x in range(1, len(b)):
    perb.append(temp*x)


temp = 100/(len(c)-1)
for x in range(1, len(c)):
    perc.append(temp*x)


temp = 100/(len(d)-1)
for x in range(1, len(d)):
    perd.append(temp*x)

temp = 100/(len(av)-1)
for x in range(1, len(av)):
    avper.append(temp*x)

plt.xlim(0, 400)
plt.ylim(0, 100)
plt.grid()


plt.plot(a, pera, color="blue", label='Node 1')
plt.plot(b, perb, color="red", label='Node 2')
plt.plot(c, perc, color="green", label='Node 3')
plt.plot(d, perd, color="cyan", label='Node 4')
plt.plot(av, avper, color="black", label='Average')



plt.legend(loc='lower right')
plt.xlabel("Time taken /Seconds")
plt.ylabel("Percentage of packets delivered")

#plt.show()

plt.savefig('fiveNodes.pgf')
