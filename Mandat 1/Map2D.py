from typing import Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches

pointScalar = 5

# Création de la figure et des axes
fig, ax = plt.subplots()

def get_point(point: Tuple[int, int]) -> Tuple[int, int]:
    return point[0] * pointScalar, point[1] * pointScalar

def get_num(num):
    return num * pointScalar

# points = ((0, 0), (4, 0), (4, 2), (3, 2), (3, 3), (0, 3))
points = ((0, 0), (4, 0), (4, 2), (3, 3), (0, 3))
xlim = (0, 5)
ylim = (0, 5)

scaled_points = [get_point(point) for point in points]
scaled_xlim = get_point(xlim)
scaled_ylim = get_point(ylim)

# Définition des coordonnées du rectangle avec le coin coupé
rectangle = patches.Polygon(scaled_points, closed=True, edgecolor='r')

# Ajout de trous
hole_point = (1, 1)
radius = 0.2
scaled_hole = get_point(hole_point)
hole = patches.Circle(scaled_hole, get_num(radius), edgecolor='b', facecolor='none')

# Ajout du rectangle aux axes
ax.add_patch(rectangle)
ax.add_patch(hole)

# Ajout de la grille avec des intervalles de 1
ax.set_xticks(range(scaled_xlim[0], scaled_xlim[1], 1))
ax.set_yticks(range(scaled_ylim[0], scaled_ylim[1], 1))
ax.grid(True)

# Définition des limites des axes
ax.set_xlim(scaled_xlim)
ax.set_ylim(scaled_ylim)

# Affichage de la figure
plt.show()

notes = [
    ["A", "B", "C", "D", "E", "F", "G"],
]
