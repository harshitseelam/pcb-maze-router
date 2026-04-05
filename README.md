# PCB Maze Router - Classical AI Course Project

Automatic PCB trace router using **State-Space Search** (Lee's Algorithm & A*) to find
shortest conflict-free paths for multiple nets on a constrained 2D grid.

---

## Problem Statement

Printed Circuit Board (PCB) design requires routing copper traces between electronic
components without any wires crossing. This project solves the **Maze Routing** problem
by automatically finding shortest conflict-free paths for multiple terminal pairs on a
2D grid, treating previously placed wires as dynamic obstacles.

---

## Classical AI Techniques Used

| Technique | Implementation |
|---|---|
| **State-Space Search (BFS)** | Lee's Algorithm - wave expansion on grid |
| **Heuristic Search** | A* with Manhattan distance heuristic |
| **Planning** | Net ordering by Manhattan distance (shortest first) |
| **Optimization** | Rip-up and reroute for failed nets |

---

## Project Structure

```
pcb-maze-router/
├── src/
│   ├── grid.py          # NumPy grid, cell constants, JSON loader
│   ├── lee.py           # Lee's Algorithm (BFS-based router)
│   ├── astar.py         # A* heuristic router
│   ├── router.py        # Multi-net orchestrator + rip-up & reroute
│   ├── visualizer.py    # PCB-styled board plots, comparisons, charts, animation
│   └── benchmarks.py    # Timing and performance comparison
├── examples/
│   ├── test_case_1.json # 10x10 grid, 3 nets (simple)
│   ├── test_case_2.json # 20x20 grid, 8 nets (medium)
│   ├── test_case_3.json # 30x30 grid, 15 nets (hard)
│   └── test_case_4.json # 20x20 grid, crossing constraint demo
├── outputs/             # Auto-generated PNGs and GIFs
├── main.py              # Entry point
├── requirements.txt
└── README.md
```

---

## Setup

```bash
git clone https://github.com/harshitseelam/pcb-maze-router
cd pcb-maze-router
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

This will:
1. Benchmark all test cases with both Lee's BFS and A*
2. Generate PCB-styled board images for each algorithm
3. Generate side-by-side Lee vs A* comparison images
4. Generate performance analysis bar charts (runtime, wire length, nodes explored)
5. Generate animated BFS wave expansion GIFs

All output files are saved to `outputs/`.

---

## Algorithm Overview

### Lee's Algorithm (BFS)

1. Start wave expansion from source cell, labeling reachable cells `1, 2, 3...`
2. Stop when target is reached
3. Backtrack from target following decreasing labels to find shortest path
4. Clean wave labels, mark path as `WIRE`

### A* Search

- Same interface as Lee's, uses a priority queue ordered by `g + h`
- `h = Manhattan distance to target`
- Explores fewer nodes on large grids with open space

### Multi-Net Strategy

- Nets sorted by Manhattan distance (shortest routed first)
- Failed nets trigger a **rip-up and reroute** pass
- Previously routed wires act as dynamic obstacles for subsequent nets

---

## Output Files

| File | Description |
|---|---|
| `test_case_X_lee.png` | PCB board routed with Lee's BFS |
| `test_case_X_astar.png` | PCB board routed with A* |
| `test_case_X_comparison.png` | Side-by-side Lee vs A* |
| `performance_analysis.png` | Bar charts comparing runtime, wire length, nodes |
| `test_case_X_wave.gif` | Animated BFS wave expansion + path backtracking |

---

## Requirements

```
numpy
matplotlib
```
