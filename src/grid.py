# src/grid.py

from typing import List, Tuple
import numpy as np

# ---------------------------------------------------------------------------
# Cell Constants
# ---------------------------------------------------------------------------
FREE     =  0
OBSTACLE = -1
WIRE     = -2

Coord = Tuple[int, int]
Path  = List[Coord]

# ---------------------------------------------------------------------------
# Grid Class
# ---------------------------------------------------------------------------
class Grid:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)

    def place_obstacle(self, r: int, c: int):
        self.board[r, c] = OBSTACLE

    def place_obstacles_bulk(self, coords: List[Coord]):
        for r, c in coords:
            self.board[r, c] = OBSTACLE

    def is_free(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols and self.board[r, c] == FREE

    def get_neighbors(self, r: int, c: int) -> List[Coord]:
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        return [(r+dr, c+dc) for dr, dc in directions
                if 0 <= r+dr < self.rows and 0 <= c+dc < self.cols]

    def mark_wire(self, path: Path):
        for r, c in path:
            self.board[r, c] = WIRE

    def clear_wave_labels(self):
        self.board[self.board > 0] = FREE

    def reset_wire(self, path: Path):
        for r, c in path:
            self.board[r, c] = FREE

    @classmethod
    def load_from_json(cls, filepath: str):
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        grid = cls(data['rows'], data['cols'])
        grid.place_obstacles_bulk([tuple(c) for c in data['obstacles']])
        nets = [tuple(tuple(p) for p in net) for net in data['nets']]
        return grid, nets

    def __repr__(self) -> str:
        symbols = {FREE: '.', OBSTACLE: '#', WIRE: 'W'}
        rows = []
        for r in range(self.rows):
            row = ''
            for c in range(self.cols):
                v = self.board[r, c]
                row += symbols.get(v, str(v % 10)) + ' '
            rows.append(row)
        return '\n'.join(rows)
