"""
Unit тесты для моделей данных (Block, Arrow)
"""

import unittest
import sys
import os

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models import Block, Arrow
from styles import Colors


class TestBlock(unittest.TestCase):
    """Тесты для модели Block"""
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.block = Block(
            block_id=1,
            name="Test Block",
            code="A0",
            element_type="Process",
            description="Test description",
            x=100,
            y=200,
            width=150,
            height=80
        )
    
    def test_block_initialization(self):
        """Тест инициализации блока"""
        self.assertEqual(self.block.id, 1)
        self.assertEqual(self.block.name, "Test Block")
        self.assertEqual(self.block.code, "A0")
        self.assertEqual(self.block.x, 100)
        self.assertEqual(self.block.y, 200)
        self.assertEqual(self.block.width, 150)
        self.assertEqual(self.block.height, 80)
    
    def test_block_to_dict(self):
        """Тест преобразования блока в словарь"""
        block_dict = self.block.to_dict()
        
        self.assertIsInstance(block_dict, dict)
        self.assertIn("name", block_dict)
        self.assertIn("code", block_dict)
        self.assertIn("x", block_dict)
        self.assertIn("y", block_dict)
        self.assertIn("width", block_dict)
        self.assertIn("height", block_dict)
    
    def test_block_update_from_dict(self):
        """Тест обновления блока из словаря"""
        update_data = {
            "name": "Updated Block",
            "code": "A1",
            "width": 200,
            "height": 100
        }
        
        self.block.update_from_dict(update_data)
        
        self.assertEqual(self.block.name, "Updated Block")
        self.assertEqual(self.block.code, "A1")
        self.assertEqual(self.block.width, 200)
        self.assertEqual(self.block.height, 100)


class TestArrow(unittest.TestCase):
    """Тесты для модели Arrow"""
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.arrow = Arrow(
            arrow_id="arrow_1",
            from_block_id="block_1",
            to_block_id="block_2",
            x1=100,
            y1=100,
            x2=200,
            y2=200
        )
    
    def test_arrow_initialization(self):
        """Тест инициализации стрелки"""
        self.assertEqual(self.arrow.id, "arrow_1")
        self.assertEqual(self.arrow.from_block_id, "block_1")
        self.assertEqual(self.arrow.to_block_id, "block_2")
        self.assertEqual(self.arrow.x1, 100)
        self.assertEqual(self.arrow.y1, 100)
        self.assertEqual(self.arrow.x2, 200)
        self.assertEqual(self.arrow.y2, 200)
    
    def test_arrow_to_dict(self):
        """Тест преобразования стрелки в словарь"""
        # Проверяем, что метод существует
        self.assertTrue(hasattr(self.arrow, 'to_dict'), "Метод to_dict должен существовать")
        
        arrow_dict = self.arrow.to_dict()
        self.assertIsInstance(arrow_dict, dict)
        self.assertIn("from_block_id", arrow_dict)
        self.assertIn("to_block_id", arrow_dict)
    
    def test_arrow_update_from_dict(self):
        """Тест обновления стрелки из словаря"""
        # Проверяем, что метод существует
        self.assertTrue(hasattr(self.arrow, 'update_from_dict'), "Метод update_from_dict должен существовать")
        
        update_data = {
            "from_block_id": "block_3",
            "to_block_id": "block_4"
        }
        
        self.arrow.update_from_dict(update_data)
        
        self.assertEqual(self.arrow.from_block_id, "block_3")
        self.assertEqual(self.arrow.to_block_id, "block_4")
    
    def test_arrow_is_connected_to_block(self):
        """Тест проверки соединения стрелки с блоком"""
        # Проверяем, что метод существует
        self.assertTrue(hasattr(self.arrow, 'is_connected_to_block'), "Метод is_connected_to_block должен существовать")
        
        self.assertTrue(self.arrow.is_connected_to_block("block_1"))
        self.assertTrue(self.arrow.is_connected_to_block("block_2"))
        self.assertFalse(self.arrow.is_connected_to_block("block_3"))


if __name__ == '__main__':
    unittest.main()

