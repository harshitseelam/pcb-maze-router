# main.py
# Entry point - runs benchmarks, generates visualizations for all test cases

import sys
import os
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src')) # without this the below imports fail

from grid import Grid
from router import route_all
from lee import route as lee_route
from astar import route as astar_route
from visualizer import (plot_pcb_board, plot_comparison, plot_performance)
from benchmarks import run_all_benchmarks, benchmark_test_case
import lee as _lee_mod
import astar as _astar_mod
import router as _router_mod

EXAMPLES_DIR = "examples"
OUTPUT_DIR   = "outputs"


def generate_visualizations(filepath, results):
    """Generate all visuals for a single test case."""
    name = os.path.splitext(os.path.basename(filepath))[0]
    grid_lee, nets = Grid.load_from_json(filepath)
    grid_astar, _  = Grid.load_from_json(filepath)

    lee_data = results['lee']
    astar_data = results['astar']

    lee_paths = lee_data['paths']
    astar_paths = astar_data['paths']

    # Mark wires on grids for proper display
    for p in lee_paths:
        if p: grid_lee.mark_wire(p)
    for p in astar_paths:
        if p: grid_astar.mark_wire(p)

    lee_metrics = {k: lee_data[k] for k in
                   ['time', 'nodes_explored'] if k in lee_data}
    astar_metrics = {k: astar_data[k] for k in
                     ['time', 'nodes_explored'] if k in astar_data}

    # Individual boards
    plot_pcb_board(grid_lee, nets, lee_paths,
                   title=f"{name} - Lee's BFS",
                   save_path=os.path.join(OUTPUT_DIR, f"{name}_lee.png"),
                   algo_name="Lee's BFS", metrics=lee_metrics)

    plot_pcb_board(grid_astar, nets, astar_paths,
                   title=f"{name} - A* Search",
                   save_path=os.path.join(OUTPUT_DIR, f"{name}_astar.png"),
                   algo_name="A* Search", metrics=astar_metrics)

    # Side-by-side comparison
    plot_comparison(filepath, nets, lee_paths, astar_paths,
                    lee_metrics, astar_metrics,
                    save_path=os.path.join(OUTPUT_DIR, f"{name}_comparison.png"))


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    test_cases = sorted([
        os.path.join(EXAMPLES_DIR, f)
        for f in os.listdir(EXAMPLES_DIR)
        if f.endswith(".json")
    ])

    # Phase 1: Benchmark all test cases
    print("\nPCB Maze Router - Benchmark & Visualization")

    all_results = run_all_benchmarks(test_cases)

    # Phase 2: Generate PCB-styled visualizations
    print("Generating visualizations...")

    for filepath in test_cases:
        name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"\n  [{name}]")
        generate_visualizations(filepath, all_results[name])

    # Phase 3: Performance comparison chart
    print(f"\nPerformance Charts")
    plot_performance(all_results, save_path=os.path.join(OUTPUT_DIR, "performance_analysis.png"))

