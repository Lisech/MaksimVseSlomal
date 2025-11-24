#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Простой скрипт для запуска автоматических тестов
"""
import sys
import os

# Добавляем путь к модулям приложения
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == '__main__':
    import unittest
    
    # Запускаем автоматизированные тесты
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем автоматизированные тесты
    test_dir = os.path.join(current_dir, 'tests', 'automated')
    automated_tests = loader.discover(test_dir, pattern='test_*.py')
    suite.addTests(automated_tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)

