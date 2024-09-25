import random

import numpy as np
import matplotlib.pyplot as plt
from Tools.scripts.parse_html5_entities import create_dict

def create_letter_slices(x):
    letters = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
    sliced_letters = []

    for letter in letters:
        for i in range(1, x + 1):
            sliced_letters.append(f"{letter}_{i}")

    return sliced_letters

def create_dict(number_of_slices, max_x, max_y):
    letters = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
    dict_name_pos = {}
    length_x = max_x // (len(letters) * number_of_slices)
    last_x_pos = 0

    for j, letter in enumerate(letters):
        for i in range(1, number_of_slices + 1):
            if j == 0 and i == 1:
                dict_name_pos[f"{letter}_{i}"] = ((0, 0),(length_x, max_y))
            else:
                dict_name_pos[f"{letter}_{i}"] = ((last_x_pos + 1, 0),(last_x_pos + length_x, max_y))
            last_x_pos += length_x
    print(dict_name_pos)
    return dict_name_pos

class Grid:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols))

        self.dict_name_pos = create_dict(2, rows -1, cols-1)

        self.dict_name_center = self.create_center_dict(self.dict_name_pos)

    def create_center_dict(self, dict_name_pos):
        center_dict = {}
        for letter, (start_pos, end_pos) in dict_name_pos.items():
            center_i = (start_pos[0] + end_pos[0]) // 2
            center_j = (start_pos[1] + end_pos[1]) // 2
            center_dict[letter] = (center_i, center_j)
        return center_dict

    def fill_grid(self):
        for letter, (start_pos, end_pos) in self.dict_name_pos.items():
            e = random.random() # correlation of the note
            for i in range(start_pos[0], end_pos[0] + 1):
                for j in range(start_pos[1], end_pos[1] + 1):
                    self.grid[i, j] = e

    def show_grid(self):
        plt.imshow(self.grid, cmap='binary', interpolation='nearest')
        # Ajouter les lettres aux positions correspondantes
        for e in self.dict_name_center:
            i, j = self.dict_name_center[e]
            plt.text(j, i, e, ha='center', va='center', color='red')
        plt.show()

# Exemple d'utilisation
grid = Grid(304, 100)
grid.fill_grid()
grid.show_grid()