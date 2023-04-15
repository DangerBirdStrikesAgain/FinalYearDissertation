import matplotlib.pyplot as plt

results = [[1, 0.12403100775193798], [1, 0.1935483870967742],[1, 0.13953488372093023],[2, 0.35664335664335667],[2,0.45454545454545453],[2,0.352112676056338],[3, 0.34356674735542],[3,0.412840124395],[3,0.35254345645876453],[4, 0.2302158273381295],[4, 0.3443252875542],[4,0.3845382956852445]]

plt.xlim(0, 5)
plt.ylim(0, 0.6)
plt.grid()
for item in results:
    plt.plot(item[0], item[1], marker="o", color="cyan")


xvals = [1, 2, 3, 4]
y = []
for x in range(0, 12, 3):
    new=(results[x][1]+results[x+1][1]+results[x+2][1])/3
    y.append(new)

print(y)

plt.plot(xvals, y, color="blue")

plt.show()