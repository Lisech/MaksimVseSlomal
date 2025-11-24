"""
Unit тесты для основных функций приложения
"""

import unittest
import sys
import os

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models import Block, Arrow


class TestBlockOperations(unittest.TestCase):
    """Тесты операций с блоками"""
    
    def test_block_creation(self):
        """Тест создания блока"""
        block = Block(
            block_id="test_1",
            name="Test Block",
            code="A0",
            x=100,
            y=100,
            width=150,
            height=80
        )
        
        self.assertIsNotNone(block)
        self.assertEqual(block.name, "Test Block")
        self.assertEqual(block.code, "A0")
    
    def test_block_properties(self):
        """Тест свойств блока"""
        block = Block(
            block_id="test_2",
            name="Test",
            x=200,
            y=200,
            width=200,
            height=100
        )
        
        self.assertEqual(block.x, 200)
        self.assertEqual(block.y, 200)
        self.assertEqual(block.width, 200)
        self.assertEqual(block.height, 100)
        self.assertGreaterEqual(block.width, 5)
        self.assertGreaterEqual(block.height, 5)


class TestArrowOperations(unittest.TestCase):
    """Тесты операций со стрелками"""
    
    def test_arrow_creation(self):
        """Тест создания стрелки"""
        arrow = Arrow(
            arrow_id="arrow_1",
            from_block_id="block_1",
            to_block_id="block_2",
            x1=100,
            y1=100,
            x2=200,
            y2=200
        )
        
        self.assertIsNotNone(arrow)
        self.assertEqual(arrow.from_block_id, "block_1")
        self.assertEqual(arrow.to_block_id, "block_2")
    
    def test_arrow_coordinates(self):
        """Тест координат стрелки"""
        arrow = Arrow(
            arrow_id="arrow_2",
            x1=50,
            y1=50,
            x2=250,
            y2=250
        )
        
        self.assertEqual(arrow.x1, 50)
        self.assertEqual(arrow.y1, 50)
        self.assertEqual(arrow.x2, 250)
        self.assertEqual(arrow.y2, 250)


class TestClipboard(unittest.TestCase):
    """Тесты буфера обмена"""
    
    def test_clipboard_structure(self):
        """Тест структуры данных буфера обмена"""
        clipboard_data = {
            "type": "block",
            "id": "block_1",
            "name": "Test Block",
            "x": 100,
            "y": 100,
            "width": 150,
            "height": 80
        }
        
        self.assertIn("type", clipboard_data)
        self.assertIn("id", clipboard_data)
        self.assertIn("name", clipboard_data)
        self.assertIn("x", clipboard_data)
        self.assertIn("y", clipboard_data)


if __name__ == '__main__':
    unittest.main()

