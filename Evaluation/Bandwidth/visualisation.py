import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'sans-serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})


y = [0.12377622377622378, 0.17857142857142858, 0.16844186046511628, 0.2786549707602339, 0.393478260869565216, 0.359602649006622516, 0.36428571428571428, 0.37053941908713693, 0.399, 0.38726087]
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

plt.xlim(0, 10.5)
plt.ylim(0, 0.8)
plt.grid()

plt.plot(x, y, color="blue", marker=".")


plt.xlabel("Number of packets generated per second")
plt.ylabel("Number of packets delivered per second")

plt.savefig('bandwidth.pgf')

#plt.show()