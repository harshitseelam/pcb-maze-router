# src/astar.py

from typing import Optional, Dict
import heapq
from grid import Grid, FREE, Coord, Path, OBSTACLE
# used in router, benchmarks, main
# Module-level counter for benchmarking
_nodes_explored = 0 # even though it is provate we are manually resetting it in benchmarks after every run

def get_nodes_explored(): # getter method
    return _nodes_explored

def _manhattan(a: Coord, b: Coord) -> int: # heuristic function, it is not admissible if diagnol movement is allowed
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def route(grid: Grid, source: Coord, target: Coord) -> Optional[Path]:
    global _nodes_explored
    sr, sc = source
    tr, tc = target

    if grid.board[sr, sc] == OBSTACLE or grid.board[tr, tc] == OBSTACLE:
        return None

    grid.board[sr, sc] = FREE
    grid.board[tr, tc] = FREE

    g_score: Dict[Coord, int] = {source: 0} # cost from source to current node but in BFS it's just wave labels
    came_from: Dict[Coord, Coord] = {}  # In BFS we are tracking parents using wave labels

    heap = [(0 + _manhattan(source, target), 0, source)]    # adding 0 for signature as source has 0 g_score
    nodes = 0

    while heap:
        f, g, current = heapq.heappop(heap)
        nodes += 1

        if current == target:
            _nodes_explored += nodes
            # Reconstruct path - traces back through came_from dict
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(source)
            path.reverse()  # we built the path in reverse i.e. from target to source so we flip it
            return path

        for neighbor in grid.get_neighbors(*current):   # *current is unpacking the tuple into arguments for get_neighbors
            if grid.board[neighbor[0], neighbor[1]] != FREE and neighbor != target:
                continue    # skip neighbors that are not free
            tentative_g = g + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + _manhattan(neighbor, target)
                heapq.heappush(heap, (f_score, tentative_g, neighbor))

    _nodes_explored += nodes
    return None

