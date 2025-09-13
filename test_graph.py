#!/usr/bin/env python3
"""Unit tests for Transport Network Graph Builder."""

import unittest
import tempfile
import os
from graph_builder1 import Graph, validate_weight, find_city_split, parse_input_to_graph


class TestGraph(unittest.TestCase):
    """Test cases for Graph class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = Graph()
    
    def test_add_node(self):
        """Test adding nodes to graph."""
        self.graph.add_node("City1")
        self.assertIn("City1", self.graph.nodes)
        self.assertIn("City1", self.graph.edges)
        self.assertEqual(self.graph.edges["City1"], {})
    
    def test_connect(self):
        """Test connecting cities with roads."""
        self.graph.add_node("City1")
        self.graph.add_node("City2")
        self.graph.connect("City1", "City2", 5)
        
        self.assertIn("City2", self.graph.edges["City1"])
        self.assertEqual(self.graph.edges["City1"]["City2"], 5)
    
    def test_connect_auto_add_node(self):
        """Test that connect automatically adds missing nodes."""
        self.graph.connect("City1", "City2", 3)
        self.assertIn("City1", self.graph.nodes)
        self.assertIn("City2", self.graph.nodes)
        self.assertEqual(self.graph.edges["City1"]["City2"], 3)
    
    def test_remove_node(self):
        """Test removing nodes and their edges."""
        self.graph.add_node("City1")
        self.graph.add_node("City2")
        self.graph.connect("City1", "City2", 5)
        self.graph.connect("City2", "City1", 3)
        
        self.graph.remove_node("City1")
        self.assertNotIn("City1", self.graph.nodes)
        self.assertNotIn("City1", self.graph.edges)
        self.assertNotIn("City1", self.graph.edges["City2"])
    
    def test_remove_edge(self):
        """Test removing specific edges."""
        self.graph.connect("City1", "City2", 5)
        self.graph.connect("City1", "City3", 3)
        
        self.graph.remove_edge("City1", "City2")
        self.assertNotIn("City2", self.graph.edges["City1"])
        self.assertIn("City3", self.graph.edges["City1"])
    
    def test_to_adjacency_lines(self):
        """Test adjacency list output format."""
        self.graph.connect("City1", "City2", 5)
        self.graph.connect("City1", "City3", 3)
        self.graph.connect("City2", "City3", 2)
        
        input_cities = ["City1", "City2", "City3"]
        lines = self.graph.to_adjacency_lines(input_cities)
        
        expected = [
            "City1: City2(5), City3(3)",
            "City2: City3(2)",
            "City3:"
        ]
        self.assertEqual(lines, expected)
    
    def test_to_json(self):
        """Test JSON output format."""
        self.graph.connect("City1", "City2", 5)
        self.graph.connect("City2", "City3", 3)
        
        input_cities = ["City1", "City2", "City3"]
        json_str = self.graph.to_json(input_cities)
        
        expected = {
            "City1": {"City2": 5},
            "City2": {"City3": 3},
            "City3": {}
        }
        self.assertEqual(eval(json_str), expected)


class TestValidation(unittest.TestCase):
    """Test cases for validation functions."""
    
    def test_validate_weight_valid(self):
        """Test valid weight validation."""
        weight = validate_weight("5", 1)
        self.assertEqual(weight, 5)
    
    def test_validate_weight_negative(self):
        """Test negative weight validation."""
        with self.assertRaises(SystemExit):
            validate_weight("-1", 1)
    
    def test_validate_weight_invalid(self):
        """Test invalid weight validation."""
        with self.assertRaises(SystemExit):
            validate_weight("abc", 1)
    
    def test_find_city_split_simple(self):
        """Test simple city name splitting."""
        tokens = ["City1", "City2"]
        valid_cities = {"City1", "City2"}
        
        city1, city2 = find_city_split(tokens, valid_cities)
        self.assertEqual(city1, "City1")
        self.assertEqual(city2, "City2")
    
    def test_find_city_split_multiword(self):
        """Test multi-word city name splitting."""
        tokens = ["New", "York", "Los", "Angeles"]
        valid_cities = {"New York", "Los Angeles"}
        
        city1, city2 = find_city_split(tokens, valid_cities)
        self.assertEqual(city1, "New York")
        self.assertEqual(city2, "Los Angeles")
    
    def test_find_city_split_not_found(self):
        """Test city split when cities not found."""
        tokens = ["City1", "City2"]
        valid_cities = {"City3", "City4"}
        
        city1, city2 = find_city_split(tokens, valid_cities)
        self.assertIsNone(city1)
        self.assertIsNone(city2)


class TestParsing(unittest.TestCase):
    """Test cases for file parsing."""
    
    def create_temp_file(self, content):
        """Create a temporary file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def tearDown(self):
        """Clean up temporary files."""
        for attr in dir(self):
            if attr.startswith('temp_file_'):
                file_path = getattr(self, attr)
                if os.path.exists(file_path):
                    os.unlink(file_path)
    
    def test_parse_simple_input(self):
        """Test parsing simple input file."""
        content = """CITIES
City1
City2
ROADS
City1 City2 5"""
        
        self.temp_file_1 = self.create_temp_file(content)
        graph, input_cities = parse_input_to_graph(self.temp_file_1)
        
        self.assertEqual(input_cities, ["City1", "City2"])
        self.assertIn("City1", graph.nodes)
        self.assertIn("City2", graph.nodes)
        self.assertEqual(graph.edges["City1"]["City2"], 5)
    
    def test_parse_multiword_cities(self):
        """Test parsing cities with spaces in names."""
        content = """CITIES
New York
Los Angeles
ROADS
New York Los Angeles 3000"""
        
        self.temp_file_2 = self.create_temp_file(content)
        graph, input_cities = parse_input_to_graph(self.temp_file_2)
        
        self.assertEqual(input_cities, ["New York", "Los Angeles"])
        self.assertEqual(graph.edges["New York"]["Los Angeles"], 3000)
    
    def test_parse_duplicate_city(self):
        """Test parsing with duplicate city names."""
        content = """CITIES
City1
City1
ROADS"""
        
        self.temp_file_3 = self.create_temp_file(content)
        with self.assertRaises(SystemExit):
            parse_input_to_graph(self.temp_file_3)
    
    def test_parse_invalid_road_format(self):
        """Test parsing with invalid road format."""
        content = """CITIES
City1
City2
ROADS
City1 City2"""
        
        self.temp_file_4 = self.create_temp_file(content)
        with self.assertRaises(SystemExit):
            parse_input_to_graph(self.temp_file_4)
    
    def test_parse_negative_weight(self):
        """Test parsing with negative weight."""
        content = """CITIES
City1
City2
ROADS
City1 City2 -5"""
        
        self.temp_file_5 = self.create_temp_file(content)
        with self.assertRaises(SystemExit):
            parse_input_to_graph(self.temp_file_5)


if __name__ == '__main__':
    unittest.main() 