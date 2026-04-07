# src/grid.py

from typing import List, Tuple
import numpy as np

# Cell Constants
FREE     =  0
OBSTACLE = -1   # using negative numbers as BFS uses positive integers to label on the same array
WIRE     = -2

Coord = Tuple[int, int]  # A pair representing one cell's position
Path  = List[Coord]      # A list of coordinates representing a wire 


# Grid Class
class Grid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)  # creating a free pcb board

    def place_obstacles_bulk(self, coords: List[Coord]):
        for r, c in coords:
            self.board[r, c] = OBSTACLE # called by load_from_json to setup the board in one shot as obstacles are already defined in json file

    def get_neighbors(self, r: int, c: int) -> List[Coord]:
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        return [(r+dr, c+dc) for dr, dc in directions
                if 0 <= r+dr < self.rows and 0 <= c+dc < self.cols]

    def mark_wire(self, path: Path):
        for r, c in path:
            self.board[r, c] = WIRE

    def clear_wave_labels(self):
        self.board[self.board > 0] = FREE # resets all cells back to 0 after a BFS run

    def reset_wire(self, path: Path):
        for r, c in path:
            self.board[r, c] = FREE # used during rip-up and reroute phase, sets a previoulsy wired path back to free

    @classmethod
    def load_from_json(cls, filepath: str): # clas refers to Grid class itself
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        grid = cls(data['rows'], data['cols']) # calls __init__ method for a new Grid instance
        grid.place_obstacles_bulk([tuple(c) for c in data['obstacles']]) # places obstacles on the board
        nets = [tuple(tuple(p) for p in net) for net in data['nets']] # converts nets to tuple of tuples
        return grid, nets

    def __repr__(self) -> str: # used while running the program to print the board
        symbols = {FREE: '.', OBSTACLE: '#', WIRE: 'W'} # mapping of values to symbols
        rows = []
        for r in range(self.rows):
            row = ''
            for c in range(self.cols):
                v = self.board[r, c]
                row += symbols.get(v, str(v % 10)) + ' '
            rows.append(row)
        return '\n'.join(rows)
