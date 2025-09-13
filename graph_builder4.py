#!/usr/bin/env python3
"""
Transport Network Graph Builder
Builds a directed weighted graph from input file and outputs adjacency list.

Usage: python3 graph_builder4.py <input_file> [--json]

Input format:
CITIES
City1
City2
City3
ROADS
City1 City2 5
City2 City3 3

Output format:
City1: City2(5), City3(10)
City2: City3(3)
City3:
"""

import sys
import json
from typing import Dict, List, Set, Tuple


class Graph:
    """Directed weighted graph for storing cities and roads."""
    
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Dict[str, int]] = {}
    
    def add_node(self, node: str) -> None:
        # ensure node is in the graph
        self.nodes.add(node)
        self.edges.setdefault(node, {})
    
    def connect(self, from_node: str, to_node: str, weight: int) -> None:
        # create directed edge with weight
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        self.edges.setdefault(from_node, {})
        self.edges[from_node][to_node] = weight
    
    def remove_node(self, node: str) -> None:
        if node in self.nodes:
            self.nodes.remove(node)
            if node in self.edges:
                del self.edges[node]
            # remove incoming edges
            for neighbor_edges in self.edges.values():
                neighbor_edges.pop(node, None)
    
    def remove_edge(self, from_node: str, to_node: str) -> None:
        if from_node in self.edges:
            self.edges[from_node].pop(to_node, None)
    
    def to_adjacency_lines(self, input_cities: List[str]) -> List[str]:
        """Convert graph to adjacency list format."""
        lines = []
        for city in input_cities:
            if city in self.edges and self.edges[city]:
                # use insertion order instead of alphabetical
                neighbors = list(self.edges[city].items())
                neighbor_str = ", ".join([f"{neighbor}({weight})" for neighbor, weight in neighbors])
                lines.append(f"{city}: {neighbor_str}")
            else:
                lines.append(f"{city}:")
        return lines
    
    def to_json(self, input_cities: List[str]) -> str:
        """Convert graph to JSON format."""
        result = {}
        for city in input_cities:
            if city in self.edges:
                result[city] = self.edges[city]
            else:
                result[city] = {}
        return json.dumps(result, indent=2)


def validate_weight(weight_str: str, line_num: int) -> int:
    """Validate and convert weight string to integer."""
    try:
        weight = int(weight_str)
        if weight < 0:
            print(f"Error: Negative weight '{weight}' on line {line_num}", file=sys.stderr)
            sys.exit(1)
        return weight
    except ValueError:
        print(f"Error: Invalid weight '{weight_str}' on line {line_num}", file=sys.stderr)
        sys.exit(1)


def find_city_split(tokens: List[str], valid_cities: Set[str]) -> Tuple[str, str]:
    """Find valid split between two cities in token list."""
    for i in range(1, len(tokens)):
        city1 = ' '.join(tokens[:i])
        city2 = ' '.join(tokens[i:])
        
        if city1 in valid_cities and city2 in valid_cities:
            return city1, city2
    
    return None, None


def parse_input_to_graph(filename: str) -> Tuple[Graph, List[str]]:
    """Parse input file and build graph."""
    graph = Graph()
    input_cities = []
    
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    
    in_cities = False
    in_roads = False
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
            
        if line == "CITIES":
            in_cities = True
            in_roads = False
            continue
        elif line == "ROADS":
            in_cities = False
            in_roads = True
            continue
        
        if in_cities:
            city = line
            if city in input_cities:
                print(f"Error: Duplicate city '{city}' on line {line_num}", file=sys.stderr)
                sys.exit(1)
            input_cities.append(city)
            graph.add_node(city)
        
        elif in_roads:
            tokens = line.split()
            if len(tokens) < 3:
                print(f"Error: Invalid road format on line {line_num}: '{line}'", file=sys.stderr)
                print("Expected: 'City1 City2 weight'", file=sys.stderr)
                sys.exit(1)
            
            weight_str = tokens[-1]
            city_tokens = tokens[:-1]
            
            city1, city2 = find_city_split(city_tokens, graph.nodes)
            if not city1 or not city2:
                print(f"Error: Could not parse cities from line {line_num}: '{line}'", file=sys.stderr)
                print("Make sure both cities are declared in the CITIES section", file=sys.stderr)
                sys.exit(1)
            
            weight = validate_weight(weight_str, line_num)
            graph.connect(city1, city2, weight)
    
    if not input_cities:
        print("Error: No CITIES section found", file=sys.stderr)
        sys.exit(1)
    
    return graph, input_cities


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python3 graph_builder4.py <input_file> [--json]", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_json = "--json" in sys.argv
    
    try:
        graph, input_cities = parse_input_to_graph(input_file)
        
        if output_json:
            print(graph.to_json(input_cities))
        else:
            adjacency_lines = graph.to_adjacency_lines(input_cities)
            for line in adjacency_lines:
                print(line)
            
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 