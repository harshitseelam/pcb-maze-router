# src/router.py

from typing import List, Tuple, Optional
from grid import Grid, WIRE, Coord, Path
from lee import route as lee_route

Net = Tuple[Coord, Coord]

def _net_priority(net: Net) -> int:
    (r1, c1), (r2, c2) = net
    return abs(r1 - r2) + abs(c1 - c2)

def route_all(grid: Grid, nets: List[Net], rip_up: bool = True
              ) -> Tuple[List[Optional[Path]], List[int]]:
    
    # Sort nets by Manhattan distance - shortest first
    indexed_nets = sorted(enumerate(nets), key=lambda x: _net_priority(x[1]))
    
    routed_paths: List[Optional[Path]] = [None] * len(nets)
    failed_indices: List[int] = []

    for original_idx, net in indexed_nets:
        source, target = net
        path = lee_route(grid, source, target)

        if path:
            routed_paths[original_idx] = path
            grid.mark_wire(path)
        else:
            failed_indices.append(original_idx)

    # Rip-up and reroute for failed nets
    if rip_up and failed_indices:
        for failed_idx in failed_indices:
            source, target = nets[failed_idx]

            # Rip up all currently routed paths and reroute everything
            for idx, path in enumerate(routed_paths):
                if path is not None:
                    grid.reset_wire(path)
                    routed_paths[idx] = None

            # Re-sort remaining nets putting failed one first
            remaining = [failed_idx] + [i for i in range(len(nets)) if i != failed_idx]
            new_failed = []

            for idx in remaining:
                path = lee_route(grid, nets[idx][0], nets[idx][1])
                if path:
                    routed_paths[idx] = path
                    grid.mark_wire(path)
                else:
                    new_failed.append(idx)

            failed_indices = new_failed
            break  # one rip-up pass per call

    return routed_paths, failed_indices
