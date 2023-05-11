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



meanTime=[]
distance=[]


results1 = [2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 17, 2, 2, 2, 2, 2, 4, 4, 2, 3, 3, 3, 3, 26, 25, 23, 22, 20, 18, 17, 27, 13, 3, 3, 3, 3, 5, 4, 30, 27, 27]
results2 = [3, 3, 3, 3, 3, 9, 4, 4, 4, 2, 5, 3, 3, 3, 3, 15, 14, 14, 12, 12, 10, 4, 3, 6, 5, 5, 5, 5, 2, 3, 19, 14, 14, 14, 5, 34, 16, 15, 10, 33, 33, 33]
results3 = [3, 16, 2, 21, 2, 2, 2, 6, 4, 4, 4, 34, 3, 19, 64, 13, 7, 3, 5, 5, 8, 3, 64, 63, 60, 9, 56, 53, 49, 47, 76, 45, 42, 53]
results4 = [15, 17, 1, 38, 37, 37, 32, 32, 88, 24, 44, 41, 41, 61, 23, 18, 18, 16, 14, 12, 9, 3, 18, 18, 15, 15, 3, 37, 29, 28, 28]
results5 = [ 15, 9, 19, 11, 7, 15, 14, 11, 10, 10, 10, 10, 6, 55, 50, 40, 31, 28, 23, 23, 23, 23, 11, 10, 7, 18, 18, 9, 7, 7, 7, 7]
results10 = [2, 2, 8, 16, 7, 7, 7, 8, 4, 15, 47, 2, 6, 37, 2, 2, 2, 2, 3, 3, 5, 5, 8, 7, 7, 7, 7, 51, 48, 47, 46, 43, 43, 34, 24, 19, 16, 80, 73, 73, 73]
results15 = [2, 5, 62, 37, 28, 72, 44, 4, 64, 5, 6, 14, 15, 4, 4, 47, 3, 15, 8, 3, 83, 83, 76, 61, 48, 36, 29, 17, 17, 11, 22, 13, 12, 51, 78, 78]
results20 = [28, 4, 19, 20, 166, 32, 24, 10, 10, 24, 123, 120, 16, 16, 16, 16, 10, 39, 47, 45, 40, 33, 25, 18, 16, 10, 9, 130, 129, 123, 106, 106]
results30 = [19, 8, 8, 3, 81, 81, 81, 142, 76, 135, 134, 67, 67, 129, 63, 62, 61, 53, 41, 86, 22, 20, 77, 7, 19, 6, 6, 6, 17, 16, 16, 11, 94, 93, 93, 93, 93]



results1.sort()
results2.sort()
results3.sort()
results4.sort()
results5.sort()
results10.sort()
results15.sort()
results20.sort()
results30.sort()

per1=[0]
per2=[0]
per3=[0]
per4=[0]
per5=[0]
per10=[0]
per15=[0]
per20=[0]
per30=[0]

temp = 100/(len(results1)-1)
for x in range(1, len(results1)):
    per1.append(temp*x)

temp = 100/(len(results2)-1)
for x in range(1, len(results2)):
    per2.append(temp*x)


temp = 100/(len(results3)-1)
for x in range(1, len(results3)):
    per3.append(temp*x)


temp = 100/(len(results4)-1)
for x in range(1, len(results4)):
    per4.append(temp*x)

temp = 100/(len(results5)-1)
for x in range(1, len(results5)):
    per5.append(temp*x)

temp = 100/(len(results10)-1)
for x in range(1, len(results10)):
    per10.append(temp*x)


temp = 100/(len(results15)-1)
for x in range(1, len(results15)):
    per15.append(temp*x)


temp = 100/(len(results20)-1)
for x in range(1, len(results20)):
    per20.append(temp*x)

temp = 100/(len(results30)-1)
for x in range(1, len(results30)):
    per30.append(temp*x)



plt.xlim(0, 175)
plt.ylim(0, 100)
plt.grid()


plt.plot(results1, per1, color="red", label='1')
plt.plot(results2, per2, color="#40a832", label='2')
plt.plot(results3, per3, color="#32a6a8", label='3')
plt.plot(results4, per4, color="#324ca8", label='4')
plt.plot(results5, per5, color="black", label='5')
plt.plot(results10, per10, color="blue", label='10')
plt.plot(results15, per15, color="cyan", label='15')
plt.plot(results20, per20, color="green", label='20')
plt.plot(results30, per30, color="#a84032", label='30')



plt.legend(loc='lower right')
plt.xlabel("Time taken / seconds")
plt.ylabel("Percentage of packets delivered")

#plt.show()

plt.savefig('sensitivity.pgf')