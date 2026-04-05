# src/astar.py

from typing import Optional, Dict
import heapq
from grid import Grid, FREE, Coord, Path, OBSTACLE

# Module-level counter for benchmarking
_nodes_explored = 0

def get_nodes_explored():
    return _nodes_explored

def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def route(grid: Grid, source: Coord, target: Coord) -> Optional[Path]:
    global _nodes_explored
    sr, sc = source
    tr, tc = target

    if grid.board[sr, sc] == OBSTACLE or grid.board[tr, tc] == OBSTACLE:
        return None

    grid.board[sr, sc] = FREE
    grid.board[tr, tc] = FREE

    g_score: Dict[Coord, int] = {source: 0}
    came_from: Dict[Coord, Coord] = {}

    heap = [(0 + _manhattan(source, target), 0, source)]
    nodes = 0

    while heap:
        f, g, current = heapq.heappop(heap)
        nodes += 1

        if current == target:
            _nodes_explored += nodes
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(source)
            path.reverse()
            return path

        for neighbor in grid.get_neighbors(*current):
            if grid.board[neighbor[0], neighbor[1]] != FREE and neighbor != target:
                continue
            tentative_g = g + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + _manhattan(neighbor, target)
                heapq.heappush(heap, (f_score, tentative_g, neighbor))

    _nodes_explored += nodes
    return None

