import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'sans-serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})

y = [0.12403100775193798, 0.13953488372093023, 0.1935483870967742, 0.2302158273381295, 0.35664335664335667, 0.3235294117647059, 0.352112676056338]
x = [1, 1.5, 2, 2.5, 3, 4, 5]

plt.xlim(0, 5.5)
plt.ylim(0, 0.6)
plt.grid()

plt.plot(x, y, color="blue", marker=".")


plt.xlabel("Number of packets generated per second")
plt.ylabel("Number of packets delivered per second")

plt.savefig('bandwidth.pgf')
