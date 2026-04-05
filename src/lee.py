# src/lee.py

from collections import deque
from typing import Optional
from grid import Grid, FREE, OBSTACLE, WIRE, Coord, Path

# Module-level counter for benchmarking
_nodes_explored = 0

def get_nodes_explored():
    return _nodes_explored

def route(grid: Grid, source: Coord, target: Coord) -> Optional[Path]:
    global _nodes_explored
    sr, sc = source
    tr, tc = target

    if grid.board[sr, sc] == OBSTACLE or grid.board[tr, tc] == OBSTACLE:
        return None

    # temporarily free source and target so wave can pass through
    grid.board[sr, sc] = FREE
    grid.board[tr, tc] = FREE

    queue = deque()
    queue.append((sr, sc))
    grid.board[sr, sc] = 1  # wave label starts at 1

    found = False
    nodes = 0
    while queue:
        r, c = queue.popleft()
        nodes += 1
        if (r, c) == (tr, tc):
            found = True
            break
        for nr, nc in grid.get_neighbors(r, c):
            if grid.board[nr, nc] == FREE:
                grid.board[nr, nc] = grid.board[r, c] + 1
                queue.append((nr, nc))

    _nodes_explored += nodes

    if not found:
        grid.clear_wave_labels()
        return None

    # Backtrack from target to source
    path = [(tr, tc)]
    r, c = tr, tc
    while (r, c) != (sr, sc):
        current_label = grid.board[r, c]
        for nr, nc in grid.get_neighbors(r, c):
            if grid.board[nr, nc] == current_label - 1:
                path.append((nr, nc))
                r, c = nr, nc
                break

    path.reverse()
    grid.clear_wave_labels()
    return path
