#!/usr/bin/env python3
"""
Transport Network Query System
Handles traffic conditions and shortest path queries using Dijkstra's algorithm.

Usage: python3 graph_query4.py <graph_file> <commands_file>
"""

import sys
import heapq
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from graph_builder4 import Graph, parse_input_to_graph


class TrafficGraph(Graph):
    """Extended graph with traffic conditions and pathfinding capabilities."""
    
    def __init__(self):
        super().__init__()
        self.traffic_map: Dict[Tuple[str, str], int] = {}
    
    def apply_traffic_report(self, from_city: str, to_city: str, delta: int) -> None:
        """Apply traffic report to modify edge weights."""
        self.traffic_map[(from_city, to_city)] = delta
    
    def get_effective_weight(self, from_city: str, to_city: str) -> Optional[int]:
        """Get effective weight including traffic conditions."""
        if from_city not in self.edges or to_city not in self.edges[from_city]:
            return None
        
        base_weight = self.edges[from_city][to_city]
        traffic_delta = self.traffic_map.get((from_city, to_city), 0)
        return max(1, base_weight + traffic_delta)
    
    def dijkstra(self, start: str, end: str) -> Tuple[List[str], int]:
        """Find shortest path using Dijkstra's algorithm with heap."""
        if start not in self.nodes or end not in self.nodes:
            return [], float('inf')
        
        pq = [(0, start, [start])]
        visited = set()
        distances = {start: 0}
        
        while pq:
            current_cost, current_city, path = heapq.heappop(pq)
            
            if current_city in visited:
                continue
                
            visited.add(current_city)
            
            if current_city == end:
                return path, current_cost
            
            for neighbor in self.edges.get(current_city, {}):
                if neighbor in visited:
                    continue
                
                effective_weight = self.get_effective_weight(current_city, neighbor)
                if effective_weight is None:
                    continue
                
                new_cost = current_cost + effective_weight
                
                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    new_path = path + [neighbor]
                    heapq.heappush(pq, (new_cost, neighbor, new_path))
        
        return [], float('inf')
    
    def find_k_paths(self, start: str, end: str, k: int) -> List[Tuple[List[str], int]]:
        """Find K shortest paths using modified Dijkstra's algorithm."""
        if start not in self.nodes or end not in self.nodes:
            return []
        
        pq = [(0, start, [start], {start})]
        paths_found = []
        visited_count = defaultdict(int)
        
        while pq and len(paths_found) < k:
            current_cost, current_city, path, visited = heapq.heappop(pq)
            
            if visited_count[current_city] >= k:
                continue
            
            if current_city == end:
                paths_found.append((path, current_cost))
                visited_count[current_city] += 1
                continue
            
            for neighbor in self.edges.get(current_city, {}):
                if neighbor in visited:
                    continue
                
                effective_weight = self.get_effective_weight(current_city, neighbor)
                if effective_weight is None:
                    continue
                
                new_cost = current_cost + effective_weight
                new_path = path + [neighbor]
                new_visited = visited | {neighbor}
                
                heapq.heappush(pq, (new_cost, neighbor, new_path, new_visited))
        
        return paths_found


def parse_traffic_report(line: str) -> Tuple[str, str, int]:
    """Parse traffic report line."""
    parts = line.split()
    if len(parts) != 4 or parts[0] != "TRAFFIC_REPORT":
        raise ValueError(f"Invalid traffic report format: {line}")
    
    from_city, to_city, delta_str = parts[1], parts[2], parts[3]
    
    if delta_str.startswith('+'):
        delta = int(delta_str[1:])
    elif delta_str.startswith('-'):
        delta = -int(delta_str[1:])
    else:
        delta = int(delta_str)
    
    return from_city, to_city, delta


def parse_query(line: str) -> Tuple[str, ...]:
    """Parse query line."""
    parts = line.split()
    if len(parts) < 2 or parts[0] != "QUERY":
        raise ValueError(f"Invalid query format: {line}")
    
    query_type = parts[1]
    
    if query_type == "SHORTEST_PATH":
        if len(parts) != 4:
            raise ValueError(f"SHORTEST_PATH requires 2 cities: {line}")
        return ("SHORTEST_PATH", parts[2], parts[3])
    
    elif query_type == "K_PATHS":
        if len(parts) != 5:
            raise ValueError(f"K_PATHS requires 2 cities and K value: {line}")
        return ("K_PATHS", parts[2], parts[3], int(parts[4]))
    
    else:
        raise ValueError(f"Unknown query type: {query_type}")


def format_path(path: List[str], cost: int) -> str:
    """Format path with arrows and cost."""
    if not path:
        return "No path found"
    
    return f"{' -> '.join(path)} (cost: {cost})"


def format_k_path(path: List[str], cost: int) -> str:
    """Format path for K_PATHS output (without 'cost:' prefix)."""
    if not path:
        return "No path found"
    
    return f"{' -> '.join(path)} ({cost})"


def process_commands(graph: TrafficGraph, commands_file: str) -> None:
    """Process commands from file."""
    try:
        with open(commands_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{commands_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{commands_file}': {e}", file=sys.stderr)
        sys.exit(1)
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
        
        try:
            if line.startswith("TRAFFIC_REPORT"):
                from_city, to_city, delta = parse_traffic_report(line)
                graph.apply_traffic_report(from_city, to_city, delta)
            
            elif line.startswith("QUERY"):
                query_parts = parse_query(line)
                
                if query_parts[0] == "SHORTEST_PATH":
                    start, end = query_parts[1], query_parts[2]
                    path, cost = graph.dijkstra(start, end)
                    
                    if path:
                        print(f"SHORTEST_PATH {start} {end}: {format_path(path, cost)}")
                    else:
                        print(f"SHORTEST_PATH {start} {end}: No path found")
                
                elif query_parts[0] == "K_PATHS":
                    start, end, k = query_parts[1], query_parts[2], query_parts[3]
                    paths = graph.find_k_paths(start, end, k)
                    
                    print(f"K_PATHS {start} {end}:")
                    if paths:
                        for i, (path, cost) in enumerate(paths, 1):
                            print(f"{i}) {format_k_path(path, cost)}")
                    else:
                        print("No paths found")
        
        except Exception as e:
            print(f"Error processing line {line_num}: {e}", file=sys.stderr)
            continue


def main():
    """Main CLI interface."""
    if len(sys.argv) != 3:
        print("Usage: python3 graph_query4.py <graph_file> <commands_file>", file=sys.stderr)
        sys.exit(1)
    
    graph_file, commands_file = sys.argv[1], sys.argv[2]
    
    try:
        base_graph, input_cities = parse_input_to_graph(graph_file)
        
        traffic_graph = TrafficGraph()
        traffic_graph.nodes = base_graph.nodes
        traffic_graph.edges = base_graph.edges
        
        process_commands(traffic_graph, commands_file)
        
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
