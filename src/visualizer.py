# src/visualizer.py
# PCB board visualization, comparison plots, performance charts, wave animation

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation
from matplotlib import patheffects
from collections import deque
from typing import List, Optional, Dict, Any

from grid import Grid, FREE, OBSTACLE, WIRE

# -----------------------------------------------------------------
# Color Palette - PCB Theme
# -----------------------------------------------------------------
PCB_BG       = '#0D1B0E'
PCB_GREEN    = '#1B5E20'
PCB_GRID     = '#256029'
COMP_BG      = '#16213E'
COMP_BD      = '#3A3A5C'
PAD_GOLD     = '#FFD700'
PAD_BORDER   = '#B8860B'
TEXT_LIGHT   = '#E8F5E9'
TEXT_DIM     = '#81C784'
STATS_BG     = '#0D3311'

TRACE_COLORS = [
    '#FF6B35', '#4FC3F7', '#FFD54F', '#E040FB', '#69F0AE',
    '#FF5252', '#40C4FF', '#FFAB40', '#B388FF', '#F4FF81',
    '#FF80AB', '#80DEEA', '#FFD740', '#EA80FC', '#A7FFEB',
]

# -----------------------------------------------------------------
# Utility
# -----------------------------------------------------------------
def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def _find_obstacle_groups(board):
    """Connected components of obstacles for IC-chip rendering."""
    rows, cols = board.shape
    visited = np.zeros((rows, cols), dtype=bool)
    groups = []
    for r in range(rows):
        for c in range(cols):
            if board[r, c] == OBSTACLE and not visited[r, c]:
                comp = []
                q = deque([(r, c)])
                visited[r, c] = True
                while q:
                    cr, cc = q.popleft()
                    comp.append((cr, cc))
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = cr+dr, cc+dc
                        if 0 <= nr < rows and 0 <= nc < cols \
                           and not visited[nr, nc] and board[nr, nc] == OBSTACLE:
                            visited[nr, nc] = True
                            q.append((nr, nc))
                groups.append(comp)
    return groups

# -----------------------------------------------------------------
# Core drawing helper (used by single + comparison plots)
# -----------------------------------------------------------------
def _draw_pcb(ax, grid, nets, routed_paths, title,
              algo_name="Lee", metrics=None):
    board = grid.board.copy()
    ax.set_xlim(-0.5, grid.cols - 0.5)
    ax.set_ylim(grid.rows - 0.5, -0.5)
    ax.set_aspect('equal')
    ax.set_facecolor(PCB_GREEN)

    # Subtle grid
    for i in range(grid.rows + 1):
        ax.axhline(y=i-0.5, color=PCB_GRID, lw=0.3, alpha=0.4, zorder=1)
    for j in range(grid.cols + 1):
        ax.axvline(x=j-0.5, color=PCB_GRID, lw=0.3, alpha=0.4, zorder=1)

    # Obstacles as IC chips
    for group in _find_obstacle_groups(board):
        rs = [r for r, c in group]
        cs = [c for r, c in group]
        r0, r1 = min(rs), max(rs)
        c0, c1 = min(cs), max(cs)
        rect = FancyBboxPatch(
            (c0-0.45, r0-0.45), (c1-c0+0.9), (r1-r0+0.9),
            boxstyle="round,pad=0.06", facecolor=COMP_BG,
            edgecolor=COMP_BD, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        cx, cy = (c0+c1)/2, (r0+r1)/2
        if len(group) >= 3:
            ax.text(cx, cy, 'IC', ha='center', va='center',
                    color='#556', fontsize=6, fontweight='bold',
                    zorder=3, alpha=0.7)

    # Copper traces
    for i, path in enumerate(routed_paths):
        if path is None:
            continue
        color = TRACE_COLORS[i % len(TRACE_COLORS)]
        xs = [c for r, c in path]
        ys = [r for r, c in path]
        ax.plot(xs, ys, color='black', lw=5, solid_capstyle='round',
                solid_joinstyle='round', alpha=0.25, zorder=4)
        ax.plot(xs, ys, color=color, lw=3.5, solid_capstyle='round',
                solid_joinstyle='round', zorder=5)
        ax.plot(xs, ys, color='white', lw=0.7, solid_capstyle='round',
                solid_joinstyle='round', alpha=0.12, zorder=6)

    # Terminal pads
    for i, net in enumerate(nets):
        (sr, sc), (tr, tc) = net
        color = TRACE_COLORS[i % len(TRACE_COLORS)]
        ok = routed_paths[i] is not None
        for (pr, pc), lbl in [((sr, sc), 'S'), ((tr, tc), 'T')]:
            outer = Circle((pc, pr), 0.38,
                           facecolor=PAD_GOLD if ok else '#444',
                           edgecolor=PAD_BORDER if ok else '#333',
                           linewidth=1.5, zorder=7)
            ax.add_patch(outer)
            inner = Circle((pc, pr), 0.22,
                           facecolor=color if ok else '#666',
                           edgecolor='none', zorder=8)
            ax.add_patch(inner)
            ax.text(pc, pr, lbl, ha='center', va='center', fontsize=5.5,
                    color='white', fontweight='bold', zorder=9,
                    path_effects=[patheffects.withStroke(
                        linewidth=1.5, foreground='black')])

    # Legend
    handles = []
    for i in range(len(nets)):
        col = TRACE_COLORS[i % len(TRACE_COLORS)]
        ok = routed_paths[i] is not None
        wl = len(routed_paths[i]) if ok else 0
        lab = f'Net {i+1} ({wl} cells)' if ok else f'Net {i+1}  FAIL'
        handles.append(Line2D([0],[0], color=col if ok else '#666',
                              linewidth=3, label=lab))
    ax.legend(handles=handles, loc='upper right', fontsize=7,
              facecolor=STATS_BG, edgecolor=PCB_GRID,
              labelcolor=TEXT_LIGHT, framealpha=0.9, borderpad=0.8)

    ax.set_title(title, fontsize=14, fontweight='bold',
                 color=TEXT_LIGHT, pad=12)

    # Stats bar
    rc = sum(1 for p in routed_paths if p is not None)
    tw = sum(len(p) for p in routed_paths if p is not None)
    parts = [f"Grid: {grid.rows}x{grid.cols}", f"Algo: {algo_name}",
             f"Routed: {rc}/{len(nets)}", f"Wire: {tw}"]
    if metrics:
        if 'time' in metrics:
            parts.append(f"Time: {metrics['time']:.4f}s")
        if 'nodes_explored' in metrics:
            parts.append(f"Nodes: {metrics['nodes_explored']}")
    ax.text(0.5, -0.02, "  |  ".join(parts), transform=ax.transAxes,
            ha='center', fontsize=8, color=TEXT_DIM, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=STATS_BG,
                      edgecolor=PCB_GRID, alpha=0.9, linewidth=0.8))

    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

# -----------------------------------------------------------------
# Public: single board
# -----------------------------------------------------------------
def plot_pcb_board(grid, nets, routed_paths, title="PCB Router",
                   save_path=None, algo_name="Lee", metrics=None):
    scale = max(grid.rows, grid.cols)
    sz = max(8, min(14, scale * 0.45))
    fig, ax = plt.subplots(figsize=(sz, sz + 0.8))
    fig.patch.set_facecolor(PCB_BG)
    _draw_pcb(ax, grid, nets, routed_paths, title, algo_name, metrics)
    plt.tight_layout(pad=1.5)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, facecolor=fig.get_facecolor(),
                    bbox_inches='tight', pad_inches=0.3)
        print(f"  Saved: {save_path}")
    plt.close()


# -----------------------------------------------------------------
# Comparison: Lee vs A* side by side
# -----------------------------------------------------------------
def plot_comparison(filepath, nets, lee_paths, astar_paths,
                    lee_metrics=None, astar_metrics=None, save_path=None):
    grid_l, _ = Grid.load_from_json(filepath)
    grid_a, _ = Grid.load_from_json(filepath)
    for p in lee_paths:
        if p: grid_l.mark_wire(p)
    for p in astar_paths:
        if p: grid_a.mark_wire(p)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    fig.patch.set_facecolor(PCB_BG)
    name = os.path.splitext(os.path.basename(filepath))[0]
    _draw_pcb(ax1, grid_l, nets, lee_paths,
              f"{name} - Lee's BFS", "Lee", lee_metrics)
    _draw_pcb(ax2, grid_a, nets, astar_paths,
              f"{name} - A* Search", "A*", astar_metrics)
    fig.suptitle(f"Algorithm Comparison - {name}", fontsize=16,
                 fontweight='bold', color=TEXT_LIGHT, y=0.98)
    plt.tight_layout(pad=1.5, rect=[0, 0, 1, 0.95])
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, facecolor=fig.get_facecolor(),
                    bbox_inches='tight', pad_inches=0.3)
        print(f"  Saved comparison: {save_path}")
    plt.close()

# -----------------------------------------------------------------
# Performance charts
# -----------------------------------------------------------------
def plot_performance(results, save_path=None):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor(PCB_BG)
    fig.suptitle("Performance Analysis - Lee's BFS vs A* Search",
                 fontsize=16, fontweight='bold', color=TEXT_LIGHT, y=1.02)

    names = list(results.keys())
    x = np.arange(len(names))
    w = 0.35
    lc, ac = '#4FC3F7', '#FF6B35'

    for ax in axes:
        ax.set_facecolor('#111')
        ax.tick_params(colors=TEXT_LIGHT, labelsize=9)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    labels = [n.replace('test_case_', 'TC') for n in names]

    # 1) Runtime
    lt = [results[n]['lee']['time'] for n in names]
    at = [results[n]['astar']['time'] for n in names]
    axes[0].bar(x-w/2, lt, w, label="Lee", color=lc, alpha=.85,
                edgecolor='white', linewidth=.5)
    axes[0].bar(x+w/2, at, w, label="A*", color=ac, alpha=.85,
                edgecolor='white', linewidth=.5)
    axes[0].set_title('Runtime (s)', color=TEXT_LIGHT, fontsize=12,
                      fontweight='bold')
    axes[0].set_xticks(x); axes[0].set_xticklabels(labels)
    axes[0].legend(facecolor='#222', edgecolor='#444',
                   labelcolor=TEXT_LIGHT, fontsize=9)
    for b, v in zip(axes[0].patches, lt + at):
        axes[0].text(b.get_x()+b.get_width()/2, b.get_height(),
                     f'{v:.4f}', ha='center', va='bottom',
                     fontsize=6, color=TEXT_LIGHT)

    # 2) Wire length
    lw = [results[n]['lee']['total_wire_length'] for n in names]
    aw = [results[n]['astar']['total_wire_length'] for n in names]
    axes[1].bar(x-w/2, lw, w, label="Lee", color=lc, alpha=.85,
                edgecolor='white', linewidth=.5)
    axes[1].bar(x+w/2, aw, w, label="A*", color=ac, alpha=.85,
                edgecolor='white', linewidth=.5)
    axes[1].set_title('Total Wire Length', color=TEXT_LIGHT,
                      fontsize=12, fontweight='bold')
    axes[1].set_xticks(x); axes[1].set_xticklabels(labels)
    axes[1].legend(facecolor='#222', edgecolor='#444',
                   labelcolor=TEXT_LIGHT, fontsize=9)
    for b, v in zip(axes[1].patches, lw + aw):
        axes[1].text(b.get_x()+b.get_width()/2, b.get_height(),
                     str(v), ha='center', va='bottom',
                     fontsize=6, color=TEXT_LIGHT)

    # 3) Nodes explored
    ln = [results[n]['lee'].get('nodes_explored', 0) for n in names]
    an = [results[n]['astar'].get('nodes_explored', 0) for n in names]
    axes[2].bar(x-w/2, ln, w, label="Lee", color=lc, alpha=.85,
                edgecolor='white', linewidth=.5)
    axes[2].bar(x+w/2, an, w, label="A*", color=ac, alpha=.85,
                edgecolor='white', linewidth=.5)
    axes[2].set_title('Nodes Explored', color=TEXT_LIGHT,
                      fontsize=12, fontweight='bold')
    axes[2].set_xticks(x); axes[2].set_xticklabels(labels)
    axes[2].legend(facecolor='#222', edgecolor='#444',
                   labelcolor=TEXT_LIGHT, fontsize=9)
    for b, v in zip(axes[2].patches, ln + an):
        axes[2].text(b.get_x()+b.get_width()/2, b.get_height(),
                     str(v), ha='center', va='bottom',
                     fontsize=6, color=TEXT_LIGHT)

    plt.tight_layout(pad=2)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, facecolor=fig.get_facecolor(),
                    bbox_inches='tight', pad_inches=0.3)
        print(f"  Saved performance chart: {save_path}")
    plt.close()

