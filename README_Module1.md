# Module 1: Transport Network Graph Builder

## Overview
This module implements a directed, weighted graph builder for transport networks. It parses input files containing cities and roads, builds a graph representation, and outputs an adjacency list format.

## Project Structure
```
transport-network/
├─ graph_builder1.py      # Main graph builder script
├─ input1.txt             # Input file with cities and roads
├─ .gitignore             # Git ignore rules
└─ README_Module1.md      # This file
```

## Features

### Graph Class
- **add_node(node)**: Add a city to the graph
- **add_edge(from_node, to_node, weight)**: Add a directed road with weight
- **remove_node(node)**: Remove a city and all its roads
- **remove_edge(from_node, to_node)**: Remove a specific road
- **to_adjacency_lines(city_order)**: Generate formatted adjacency list output

### Input Parser
- Parses files with `CITIES` and `ROADS` sections
- Validates city names and road weights
- Handles duplicate cities and unknown cities in roads
- Provides clear error messages with line numbers

### CLI Interface
- Simple command-line interface: `python3 graph_builder1.py input1.txt`
- Outputs adjacency list format: `City1: City2(5), City4(10)`
- Preserves city order from input file
- Sorts neighbors for stable output

## Input Format

The input file should have the following structure:
```
CITIES
City1
City2
City3
ROADS
City1 City2 5
City1 City3 10
City2 City3 3
```

### Requirements:
- Cities section must come first
- Each road entry must have exactly 3 tokens: `from_city to_city weight`
- Weights must be non-negative integers
- All cities in roads must be declared in the cities section

## Output Format

The program outputs an adjacency list where each line shows a city and its neighbors:
```
City1: City2(5), City3(10)
City2: City3(3)
City3:
```

## Error Handling

The program provides comprehensive error handling:
- File not found errors
- Invalid road format (wrong number of tokens)
- Unknown cities in road definitions
- Negative or invalid weights
- Duplicate city declarations
- Missing CITIES section

All errors include line numbers and descriptive messages, with exit code 1.

## Usage Examples

### Basic Usage
```bash
python3 graph_builder1.py input1.txt
```

### Example Input (input1.txt)
```
CITIES
New York
Boston
Chicago
ROADS
New York Boston 200
New York Chicago 800
Boston Chicago 1000
```

### Example Output
```
New York: Boston(200), Chicago(800)
Boston: Chicago(1000)
Chicago:
```

## Design Decisions

1. **Directed Graph**: Roads are directional (City1 → City2 ≠ City2 → City1)
2. **Weighted Edges**: Each road has a distance/weight value
3. **Order Preservation**: Output maintains the city order from input
4. **Stable Output**: Neighbors are sorted alphabetically for consistent results
5. **Overwrite Behavior**: If a road appears multiple times, the last occurrence wins

## Future Modules

This Graph class is designed to be reusable for:
- **Module 2**: Graph queries and pathfinding
- **Module 3**: Scheduling and optimization

The clean interface allows other modules to import and extend the Graph functionality without modification. 