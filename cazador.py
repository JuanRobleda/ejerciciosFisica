import math

g = 9.81

x_mono = 15
y_mono = 20
y_cazador = 1.8
v0 = 5

theta = math.atan((y_mono - y_cazador) / x_mono)

vx = v0 * math.cos(theta)
vy = v0 * math.sin(theta)

print("Angulo:", math.degrees(theta), "grados")

tiempos = [0, 0.5, 1, 1.5, 2, 2.5, 3]

print("\nt\tY_mono\tX_proy\tY_proy")

for t in tiempos:
    ymono = y_mono - 0.5 * g * t**2
    xproy = vx * t
    yproy = y_cazador + vy * t - 0.5 * g * t**2

    print(f"{t:.1f}\t{ymono:.2f}\t{xproy:.2f}\t{yproy:.2f}")