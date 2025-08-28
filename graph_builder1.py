#!/usr/bin/env python3
"""
Module 1: Graph Builder
Builds a directed, weighted graph from input file and outputs adjacency list.

ORGANIZATION:
============
1. Graph Class (lines 10-60): Core data structure implementation
2. Input Parsing (lines 62-150): File reading and validation logic
3. Main Interface (lines 152-183): CLI handling and program flow

USAGE:
======
python3 graph_builder1.py input1.txt

INPUT FORMAT:
============
CITIES
City1
City2
City3
ROADS
City1 City2 5
City2 City3 3

OUTPUT FORMAT:
=============
City1: City2(5), City3(10)
City2: City3(3)
City3:
"""

import sys
from typing import Dict, List, Set, Tuple


# ============================================================================
# GRAPH DATA STRUCTURE IMPLEMENTATION
# ============================================================================
class Graph:
    """
    A directed, weighted graph implementation.
    
    DATA STRUCTURE:
    - nodes: Set of all city names
    - edges: Dictionary mapping each city to its outgoing edges
             Format: {city_name: {neighbor_city: weight}}
    
    EXAMPLE:
    nodes = {"City1", "City2", "City3"}
    edges = {
        "City1": {"City2": 5, "City3": 10},
        "City2": {"City3": 3},
        "City3": {}
    }
    """
    
    def __init__(self):
        """Initialize an empty graph."""
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Dict[str, int]] = {}  # node -> {neighbor: weight}
    
    def add_node(self, node: str) -> None:
        """
        Add a node to the graph.
        
        PARAMETERS:
        - node: Name of the city to add
        
        EFFECT:
        - Adds city to nodes set
        - Creates empty edge dictionary for the city
        """
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = {}
    
    def add_edge(self, from_node: str, to_node: str, weight: int) -> None:
        """
        Add a directed edge with weight from from_node to to_node.
        
        PARAMETERS:
        - from_node: Starting city
        - to_node: Destination city  
        - weight: Distance/weight of the road
        
        EFFECT:
        - Creates directed edge from from_node to to_node
        - If from_node doesn't exist in edges, creates it
        """
        if from_node not in self.edges:
            self.edges[from_node] = {}
        self.edges[from_node][to_node] = weight
    
    def remove_node(self, node: str) -> None:
        """
        Remove a node and all its incident edges.
        
        PARAMETERS:
        - node: Name of the city to remove
        
        EFFECT:
        - Removes city from nodes set
        - Removes all outgoing edges from this city
        - Removes all incoming edges to this city from other cities
        """
        if node in self.nodes:
            self.nodes.remove(node)
            if node in self.edges:
                del self.edges[node]
            # Remove all edges pointing to this node
            for neighbor_edges in self.edges.values():
                if node in neighbor_edges:
                    del neighbor_edges[node]
    
    def remove_edge(self, from_node: str, to_node: str) -> None:
        """
        Remove the edge from from_node to to_node.
        
        PARAMETERS:
        - from_node: Starting city
        - to_node: Destination city
        
        EFFECT:
        - Removes only the specific directed edge
        - Does not affect other edges or nodes
        """
        if from_node in self.edges and to_node in self.edges[from_node]:
            del self.edges[from_node][to_node]
    
    def to_adjacency_lines(self, city_order: List[str]) -> List[str]:
        """
        Convert graph to adjacency list format, preserving city order.
        
        PARAMETERS:
        - city_order: List of cities in the order they should appear in output
        
        RETURNS:
        - List of formatted strings: "City: Neighbor1(weight1), Neighbor2(weight2)"
        
        ALGORITHM:
        1. Iterate through cities in specified order
        2. For each city, get its neighbors and weights
        3. Sort neighbors alphabetically for stable output
        4. Format as "City: Neighbor1(weight1), Neighbor2(weight2)"
        5. If city has no neighbors, output "City:"
        """
        lines = []
        for city in city_order:
            if city in self.edges and self.edges[city]:
                # Sort neighbors for stable output
                neighbors = sorted(self.edges[city].items(), key=lambda x: x[0])
                neighbor_str = ", ".join([f"{neighbor}({weight})" for neighbor, weight in neighbors])
                lines.append(f"{city}: {neighbor_str}")
            else:
                lines.append(f"{city}:")
        return lines


# ============================================================================
# INPUT FILE PARSING AND VALIDATION
# ============================================================================
def parse_input_to_graph(filename: str) -> Tuple[Graph, List[str]]:
    """
    Parse input file and build graph.
    
    PARAMETERS:
    - filename: Path to input file
    
    RETURNS:
    - Tuple of (graph, city_order) where city_order preserves input order
    
    ALGORITHM:
    1. Read file line by line
    2. Parse CITIES section: add each city to graph and track order
    3. Parse ROADS section: add each road as directed edge
    4. Validate all data during parsing
    
    ERROR HANDLING:
    - File not found
    - Invalid road format
    - Duplicate cities
    - Negative weights
    - Cities not declared in CITIES section
    """
    graph = Graph()
    city_order = []
    
    # File reading with error handling
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    
    # State tracking for parsing
    in_cities = False
    in_roads = False
    
    # Parse file line by line
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        # Section headers
        if line == "CITIES":
            in_cities = True
            in_roads = False
            continue
        elif line == "ROADS":
            in_cities = False
            in_roads = True
            continue
        
        # Parse CITIES section
        if in_cities:
            # Parse city names (can contain spaces)
            city = line
            if city in city_order:
                print(f"Error: Duplicate city '{city}' on line {line_num}", file=sys.stderr)
                sys.exit(1)
            city_order.append(city)
            graph.add_node(city)
        
        # Parse ROADS section
        elif in_roads:
            # Parse road entries: "City1 City2 weight"
            # Split the line and find the weight (last token)
            tokens = line.split()
            if len(tokens) < 3:
                print(f"Error: Invalid road format on line {line_num}: '{line}'", file=sys.stderr)
                print("Expected: 'City1 City2 weight'", file=sys.stderr)
                sys.exit(1)
            
            # Last token is the weight
            weight_str = tokens[-1]
            # Everything before the last token is the cities
            city_tokens = tokens[:-1]
            
            # SMART CITY PARSING ALGORITHM:
            # Since city names can contain spaces, we need to find the split
            # between the two cities. We try all possible splits and check
            # if both resulting cities exist in our graph.
            city1_found = False
            city2_found = False
            
            for i in range(1, len(city_tokens)):
                city1 = ' '.join(city_tokens[:i])
                city2 = ' '.join(city_tokens[i:])
                
                if city1 in graph.nodes and city2 in graph.nodes:
                    city1_found = True
                    city2_found = True
                    break
            
            if not (city1_found and city2_found):
                print(f"Error: Could not parse cities from line {line_num}: '{line}'", file=sys.stderr)
                print("Make sure both cities are declared in the CITIES section", file=sys.stderr)
                sys.exit(1)
            
            # Validate weight
            try:
                weight = int(weight_str)
                if weight < 0:
                    print(f"Error: Negative weight '{weight}' on line {line_num}", file=sys.stderr)
                    sys.exit(1)
            except ValueError:
                print(f"Error: Invalid weight '{weight_str}' on line {line_num}", file=sys.stderr)
                sys.exit(1)
            
            # Add the validated edge to the graph
            graph.add_edge(city1, city2, weight)
    
    # Final validation
    if not city_order:
        print("Error: No CITIES section found", file=sys.stderr)
        sys.exit(1)
    
    return graph, city_order


# ============================================================================
# MAIN PROGRAM INTERFACE
# ============================================================================
def main():
    """
    Main CLI interface.
    
    PROGRAM FLOW:
    1. Validate command line arguments
    2. Parse input file into graph
    3. Convert graph to adjacency list format
    4. Print results
    
    USAGE:
    python3 graph_builder1.py <input_file>
    
    ERROR HANDLING:
    - Wrong number of arguments
    - File parsing errors
    - Unexpected exceptions
    """
    # Validate command line arguments
    if len(sys.argv) != 2:
        print("Usage: python3 graph_builder1.py <input_file>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Parse input and build graph
        graph, city_order = parse_input_to_graph(input_file)
        
        # Convert to adjacency list format
        adjacency_lines = graph.to_adjacency_lines(city_order)
        
        # Print output
        for line in adjacency_lines:
            print(line)
            
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main() 