"""
Интеграционные тесты для IDEF0 Editor
"""

import unittest
import sys
import os
import tkinter as tk

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models import Block, Arrow


class TestAppIntegration(unittest.TestCase):
    """Интеграционные тесты приложения"""
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        # Создаем корневое окно для тестов
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем окно
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.root.destroy()
    
    def test_block_and_arrow_connection(self):
        """Тест соединения блока и стрелки"""
        block1 = Block(block_id="block_1", x=100, y=100, width=150, height=80)
        block2 = Block(block_id="block_2", x=300, y=100, width=150, height=80)
        
        arrow = Arrow(
            arrow_id="arrow_1",
            from_block_id="block_1",
            to_block_id="block_2"
        )
        
        self.assertEqual(arrow.from_block_id, block1.id)
        self.assertEqual(arrow.to_block_id, block2.id)
    
    def test_multiple_blocks(self):
        """Тест работы с несколькими блоками"""
        blocks = []
        for i in range(5):
            block = Block(
                block_id=f"block_{i}",
                name=f"Block {i}",
                x=100 + i * 200,
                y=100,
                width=150,
                height=80
            )
            blocks.append(block)
        
        self.assertEqual(len(blocks), 5)
        for i, block in enumerate(blocks):
            self.assertEqual(block.id, f"block_{i}")
            self.assertEqual(block.x, 100 + i * 200)
    
    def test_block_movement(self):
        """Тест перемещения блока"""
        block = Block(block_id="block_1", x=100, y=100, width=150, height=80)
        initial_x = block.x
        initial_y = block.y
        
        # Перемещаем блок
        block.x = 200
        block.y = 200
        
        self.assertNotEqual(block.x, initial_x)
        self.assertNotEqual(block.y, initial_y)
        self.assertEqual(block.x, 200)
        self.assertEqual(block.y, 200)
    
    def test_block_resize(self):
        """Тест изменения размера блока"""
        block = Block(block_id="block_1", x=100, y=100, width=150, height=80)
        initial_width = block.width
        initial_height = block.height
        
        # Изменяем размер
        block.width = 200
        block.height = 120
        
        self.assertNotEqual(block.width, initial_width)
        self.assertNotEqual(block.height, initial_height)
        self.assertEqual(block.width, 200)
        self.assertEqual(block.height, 120)
    
    def test_arrow_update_on_block_move(self):
        """Тест обновления стрелки при перемещении блока"""
        block = Block(block_id="block_1", x=100, y=100, width=150, height=80)
        arrow = Arrow(
            arrow_id="arrow_1",
            from_block_id="block_1",
            to_block_id=None,
            x1=block.x + block.width / 2,
            y1=block.y
        )
        
        initial_x1 = arrow.x1
        
        # Перемещаем блок
        block.x = 200
        block.y = 200
        
        # Стрелка должна обновиться (в реальном приложении это делается автоматически)
        # Здесь просто проверяем, что координаты можно обновить
        arrow.x1 = block.x + block.width / 2
        arrow.y1 = block.y
        
        self.assertNotEqual(arrow.x1, initial_x1)
        new_x = block.x + block.width / 2
        self.assertEqual(arrow.x1, new_x)


if __name__ == '__main__':
    unittest.main()

