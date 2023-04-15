import matplotlib.pyplot as plt
import numpy as np

meanTime=[]
distance=[]
results0 = [6, 30, 3, 11, 6, 6, 45, 44, 36, 74, 33, 32, 22, 19, 57, 10, 7, 7, 7, 40, 6, 6, 12, 9, 26, 24, 24, 13, 9, 27, 27, 26, 14, 14, 9, 3, 9, 9, 9, 19, 14, 8, 5, 16, 14, 13, 13, 5, 7, 6, 4, 8, 8, 4, 8, 6, 5, 8, 3, 12, 4, 5, 14, 5, 4, 4]
meanTime.append(sum(results0)/len(results0))
distance.append(0)

results100 = [76, 58, 23, 21, 21, 14, 10, 39, 6, 6, 59, 6, 6, 22, 22, 15, 13, 13, 12, 10, 9, 21, 12, 12, 12, 52, 22, 14, 137, 135, 135, 128, 119, 117, 105, 103, 103, 5, 2, 22, 22, 22, 15, 78, 8, 71, 10, 9, 14, 14, 73, 6, 15, 15, 15, 13, 7, 57, 7, 50, 48, 47, 32, 27, 20, 11, 4, 4, 7, 6]


results10 = [5, 6, 6, 3, 10, 8, 8, 8, 7, 3, 3, 3, 7, 4, 4, 5, 6, 6, 6, 36, 30, 27, 17, 8, 6, 19, 19, 18, 17, 10, 21, 20, 15, 14, 5, 4, 4, 5,  27, 27, 27, 25, 24, 21, 92, 19, 15, 13, 84, 46, 9, 9, 14,  11, 7, 6, 7, 44, 8, 8, 18, 16, 14, 11]
meanTime.append(sum(results10)/len(results10))
distance.append(10)
meanTime.append(sum(results100)/len(results100))
distance.append(100)
results250 = [303, 78, 39, 333, 12, 47, 117, 18, 210, 58, 73, 333, 16, 34, 165, 45, 371, 168, 399, 36, 18, 360, 45, 110, 111, 358, 284, 320, 65, 20, 186, 71, 301, 395, 31, 82, 340, 101, 288, 115, 240, 217, 48, 245, 59, 37, 26, 18, 24, 24, 48, 43, 73, 218, 98, 270, 360, 297]
meanTime.append(sum(results250)/len(results250))
distance.append(250)

results500 = [249, 385, 313, 267, 32, 69, 295, 342, 302, 56, 27, 29, 338, 65, 208, 45, 455, 487, 139, 66, 49, 95, 211, 117, 163, 154, 327, 300, 23, 477, 206, 134, 46, 31, 309, 20, 379, 299, 421, 298, 326, 258, 342, 338, 284, 340, 348, 150, 210, 267, 385, 494, 436, 169, 332, 161]
meanTime.append(sum(results500)/len(results500))
distance.append(500)

plt.xlim(0, 510)
plt.ylim(0, 520)
plt.grid()
for item in results0:
    plt.plot(0, item, marker="o", color="cyan")
for item in results10:
    plt.plot(10, item, marker="o", color="cyan")
for item in results100:
    plt.plot(100, item, marker="o", color="cyan")
for item in results250:
    plt.plot(250, item, marker="o", color="cyan")
for item in results500:
    plt.plot(500, item, marker="o", color="cyan")

plt.plot(distance, meanTime, color="blue")
print(meanTime)
print(f"[{np.std(results0)}, {np.std(results10)}, {np.std(results100)}, {np.std(results250)}, {np.std(results500)}]")



plt.show()