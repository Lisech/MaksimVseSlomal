#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт настройки Git конфигурации
"""

import subprocess
import sys

def main():
    print("Настройка Git конфигурации...")
    print()
    
    # Настройка имени пользователя
    try:
        subprocess.run(
            ["git", "config", "--global", "user.name", "jawa350m1"],
            check=True,
            capture_output=True
        )
        print("[OK] Имя пользователя установлено: jawa350m1")
    except subprocess.CalledProcessError as e:
        print(f"[ОШИБКА] Не удалось установить имя пользователя: {e}")
        return 1
    
    # Настройка email
    try:
        subprocess.run(
            ["git", "config", "--global", "user.email", "jawa350m1@gmail.com"],
            check=True,
            capture_output=True
        )
        print("[OK] Email установлен: jawa350m1@gmail.com")
    except subprocess.CalledProcessError as e:
        print(f"[ОШИБКА] Не удалось установить email: {e}")
        return 1
    
    # Проверка настроек
    print()
    print("=" * 50)
    print("Git конфигурация успешно настроена!")
    print("=" * 50)
    print()
    print("Проверка настроек:")
    
    try:
        result_name = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True,
            check=True
        )
        result_email = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Имя: {result_name.stdout.strip()}")
        print(f"Email: {result_email.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при проверке настроек: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nОперация прервана пользователем.")
        sys.exit(1)

