# src/benchmarks.py
# Timing and performance comparison for Lee's BFS vs A*

import os
import sys
import time
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(__file__))

from grid import Grid
from router import route_all
from lee import route as lee_route, get_nodes_explored as lee_nodes
from astar import route as astar_route, get_nodes_explored as astar_nodes
# We cannot write a modules internal variables without importing them
import lee as _lee_mod
import astar as _astar_mod
import router as _router_mod
"""
Runs both A* and Lee on every test case by precisely calculating the time consumed by
each algorithm, counting the nodes explored and packages the entire information in a
dictionary so that visualizer can use it for output images
"""


def benchmark_test_case(filepath: str, algorithm: str = 'lee') -> Dict:
    """Run one algorithm on a test case and collect metrics."""
    grid, nets = Grid.load_from_json(filepath)  # Fresh board every time as old borad may have routed wire as obstacles

    # Reset node counters - resetting both just for safety
    _lee_mod._nodes_explored = 0
    _astar_mod._nodes_explored = 0

    # Swap algorithm in the router
    if algorithm == 'astar':
        _router_mod.lee_route = astar_route # this module injects astar_route to router during runtime aka MONKEY PATCHING
    else:
        _router_mod.lee_route = lee_route

    start = time.perf_counter() # highest resolution timer available in python
    routed_paths, failed = route_all(grid, nets)    # we are not timing grid loading or counter resets
    elapsed = time.perf_counter() - start

    # Restore default
    _router_mod.lee_route = lee_route

    routed_count = sum(1 for p in routed_paths if p is not None)
    total_wire = sum(len(p) for p in routed_paths if p is not None)
    nodes = astar_nodes() if algorithm == 'astar' else lee_nodes()

    return {
        'algorithm': algorithm,
        'time': elapsed,
        'routed': routed_count,
        'total_nets': len(nets),
        'total_wire_length': total_wire,
        'nodes_explored': nodes,
        'paths': routed_paths,
        'failed': failed,
    }


def run_all_benchmarks(test_files: List[str]) -> Dict:
    """Run both algorithms on all test cases. Returns nested dict."""
    results = {}
    for filepath in test_files:
        name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"\n  Benchmarking {name}...")
        lee_result = benchmark_test_case(filepath, 'lee')
        astar_result = benchmark_test_case(filepath, 'astar')
        results[name] = {'lee': lee_result, 'astar': astar_result}
        print(f"    Lee:  {lee_result['routed']}/{lee_result['total_nets']} routed, "
              f"{lee_result['time']:.4f}s, {lee_result['nodes_explored']} nodes")
        print(f"    A*:   {astar_result['routed']}/{astar_result['total_nets']} routed, "
              f"{astar_result['time']:.4f}s, {astar_result['nodes_explored']} nodes")
    return results
