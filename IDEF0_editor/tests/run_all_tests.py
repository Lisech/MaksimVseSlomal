"""
Единый файл запуска всех тестов IDEF0 Editor
Включает автоматические тесты и ручное тестирование
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import unittest
import sys
import os
import threading
import io
import json
import re
import datetime
import traceback

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============================================================================
# ПАРСЕР РУЧНЫХ ТЕСТОВ (встроенный)
# ============================================================================

class ManualTestParser:
    """Парсит файл MANUAL_TESTING.md и извлекает структуру тестов"""
    
    def __init__(self, md_file_path):
        self.md_file_path = md_file_path
        self.tests = []
        self._parse()
    
    def _parse(self):
        """Парсит markdown файл и извлекает тесты"""
        if not os.path.exists(self.md_file_path):
            return
        
        with open(self.md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разбиваем на секции по ##
        sections = re.split(r'^## (\d+)\.\s+(.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 3):
            if i + 1 < len(sections):
                section_num = sections[i]
                section_title = sections[i + 1]
                section_content = sections[i + 2] if i + 2 < len(sections) else ""
                
                # Извлекаем подразделы (###)
                subsections = re.split(r'^### (\d+\.\d+)\s+(.+)$', section_content, flags=re.MULTILINE)
                
                for j in range(1, len(subsections), 3):
                    if j + 1 < len(subsections):
                        subsection_num = subsections[j]
                        subsection_title = subsections[j + 1]
                        subsection_content = subsections[j + 2] if j + 2 < len(subsections) else ""
                        
                        # Извлекаем шаги и ожидаемый результат
                        steps_match = re.search(r'\*\*Шаги:\*\*\s*\n((?:\d+\.\s+.*\n?)+)', subsection_content)
                        expected_match = re.search(r'\*\*Ожидаемый результат:\*\*\s*\n((?:- .*\n?)+)', subsection_content)
                        
                        steps = []
                        expected = []
                        
                        if steps_match:
                            steps_text = steps_match.group(1)
                            steps = [s.strip() for s in re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|\Z)', steps_text, re.DOTALL)]
                        
                        if expected_match:
                            expected_text = expected_match.group(1)
                            expected = [e.strip()[2:] for e in expected_text.split('\n') if e.strip().startswith('-')]
                        
                        test_item = {
                            'id': f"{section_num}.{subsection_num}",
                            'section': section_num,
                            'subsection': subsection_num,
                            'title': f"{section_num}.{subsection_num} {subsection_title}",
                            'section_title': section_title,
                            'subsection_title': subsection_title,
                            'steps': steps,
                            'expected': expected,
                            'full_content': subsection_content.strip()
                        }
                        
                        self.tests.append(test_item)
    
    def get_tests(self):
        """Возвращает список всех тестов"""
        return self.tests
    
    def get_test_by_id(self, test_id):
        """Возвращает тест по ID"""
        for test in self.tests:
            if test['id'] == test_id:
                return test
        return None
    
    def get_tests_by_section(self, section_num):
        """Возвращает все тесты из указанной секции"""
        return [test for test in self.tests if test['section'] == section_num]


# ============================================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ ДЛЯ ТЕСТИРОВАНИЯ
# ============================================================================

class TestRunnerApp:
    """GUI приложение для запуска всех тестов"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("IDEF0 Editor - Система тестирования")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f0f0f0")
        
        # Переменные для результатов
        self.test_results = {}
        self.is_running = False
        
        # Результаты ручного тестирования
        self.manual_test_results = {}
        self.manual_test_parser = None
        self.manual_tests = []
        self.current_test_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="IDEF0 Editor - Система тестирования",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Основной контейнер с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка автоматических тестов
        self.auto_test_frame = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.auto_test_frame, text="Автоматические тесты")
        
        # Вкладка ручного тестирования
        self.manual_test_frame = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.manual_test_frame, text="Ручное тестирование")
        
        # Настраиваем интерфейс автоматических тестов
        self.setup_auto_test_ui(self.auto_test_frame)
        
        # Настраиваем интерфейс ручного тестирования
        self.setup_manual_test_ui(self.manual_test_frame)
    
    def setup_auto_test_ui(self, parent):
        """Настройка интерфейса автоматических тестов"""
        # Панель кнопок
        buttons_frame = tk.Frame(parent, bg="#f0f0f0")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки запуска тестов
        self.btn_unit = tk.Button(
            buttons_frame,
            text="▶ Unit тесты",
            command=lambda: self.run_tests("unit"),
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_unit.pack(side=tk.LEFT, padx=5)
        
        self.btn_integration = tk.Button(
            buttons_frame,
            text="▶ Интеграционные тесты",
            command=lambda: self.run_tests("integration"),
            bg="#9b59b6",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_integration.pack(side=tk.LEFT, padx=5)
        
        self.btn_automated = tk.Button(
            buttons_frame,
            text="▶ Автоматические UI тесты",
            command=lambda: self.run_tests("automated"),
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_automated.pack(side=tk.LEFT, padx=5)
        
        self.btn_all = tk.Button(
            buttons_frame,
            text="▶ Все тесты",
            command=lambda: self.run_tests("all"),
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_all.pack(side=tk.LEFT, padx=5)
        
        # Кнопка открытия руководства по ручному тестированию
        self.btn_manual = tk.Button(
            buttons_frame,
            text="📖 Руководство",
            command=self.open_manual_guide,
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_manual.pack(side=tk.LEFT, padx=5)
        
        # Кнопка очистки вывода
        self.btn_clear = tk.Button(
            buttons_frame,
            text="🗑 Очистить",
            command=self.clear_output,
            bg="#95a5a6",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сохранения результатов
        self.btn_save = tk.Button(
            buttons_frame,
            text="💾 Сохранить результаты",
            command=self.save_results,
            bg="#16a085",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_frame = tk.Frame(parent, bg="#ecf0f1", relief=tk.SUNKEN, bd=1)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Готов к запуску тестов",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Segoe UI", 9),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_label.pack(fill=tk.X)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(
            parent,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Область вывода результатов
        output_label = tk.Label(
            parent,
            text="Результаты тестов:",
            bg="#f0f0f0",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold"),
            anchor=tk.W
        )
        output_label.pack(fill=tk.X, pady=(0, 5))
        
        # Текстовое поле с прокруткой для вывода
        self.output_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#ffffff",
            fg="#2c3e50",
            relief=tk.SUNKEN,
            bd=1
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Панель статистики
        stats_frame = tk.Frame(parent, bg="#ecf0f1", relief=tk.SUNKEN, bd=1)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Статистика: Запустите тесты для просмотра результатов",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Segoe UI", 9),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.stats_label.pack(fill=tk.X)
    
    def setup_manual_test_ui(self, parent):
        """Настройка интерфейса ручного тестирования"""
        # Загружаем тесты из файла
        manual_path = os.path.join(os.path.dirname(__file__), "manual", "MANUAL_TESTING.md")
        self.manual_tests = []
        self.manual_test_parser = None
        
        if os.path.exists(manual_path):
            try:
                self.manual_test_parser = ManualTestParser(manual_path)
                self.manual_tests = self.manual_test_parser.get_tests()
                if not self.manual_tests:
                    print("Предупреждение: Не найдено тестов в файле MANUAL_TESTING.md")
            except Exception as e:
                print(f"Ошибка при загрузке ручных тестов: {e}")
                print(traceback.format_exc())
                self.manual_tests = []
        else:
            print(f"Файл не найден: {manual_path}")
        
        # Загружаем сохраненные результаты
        self.load_manual_test_results()
        
        # Контейнер с двумя колонками
        container = tk.Frame(parent, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - список тестов
        left_panel = tk.Frame(container, bg="#ffffff", relief=tk.SUNKEN, bd=1, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Заголовок списка тестов
        list_header = tk.Label(
            left_panel,
            text="Список тестов",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            pady=10
        )
        list_header.pack(fill=tk.X)
        
        # Список тестов с прокруткой
        list_frame = tk.Frame(left_panel, bg="#ffffff")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.test_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#2c3e50",
            selectbackground="#3498db",
            selectforeground="white",
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.test_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.test_listbox.yview)
        
        # Заполняем список тестов
        for test in self.manual_tests:
            test_id = test['id']
            status = self.manual_test_results.get(test_id, None)
            prefix = "✓ " if status == "passed" else "✗ " if status == "failed" else "○ "
            color = "#27ae60" if status == "passed" else "#e74c3c" if status == "failed" else "#2c3e50"
            self.test_listbox.insert(tk.END, f"{prefix}{test['title']}")
            self.test_listbox.itemconfig(self.test_listbox.size() - 1, {'fg': color})
        
        # Привязываем событие выбора
        self.test_listbox.bind('<<ListboxSelect>>', self.on_test_select)
        
        # Правая панель - инструкции и кнопки
        right_panel = tk.Frame(container, bg="#f0f0f0")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Заголовок инструкций
        instruction_header = tk.Label(
            right_panel,
            text="Инструкция по тестированию",
            bg="#2c3e50",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            pady=10
        )
        instruction_header.pack(fill=tk.X)
        
        # Область с инструкциями
        self.instruction_text = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#2c3e50",
            relief=tk.SUNKEN,
            bd=1,
            state=tk.DISABLED
        )
        self.instruction_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель кнопок для отметки результатов
        button_panel = tk.Frame(right_panel, bg="#f0f0f0")
        button_panel.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_pass = tk.Button(
            button_panel,
            text="✓ Тест пройден",
            command=lambda: self.mark_test_result("passed"),
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_pass.pack(side=tk.LEFT, padx=5)
        
        self.btn_fail = tk.Button(
            button_panel,
            text="✗ Тест провален",
            command=lambda: self.mark_test_result("failed"),
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_fail.pack(side=tk.LEFT, padx=5)
        
        self.btn_reset = tk.Button(
            button_panel,
            text="↺ Сбросить",
            command=lambda: self.mark_test_result(None),
            bg="#95a5a6",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_reset.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сохранения результатов ручного тестирования
        self.btn_save_manual = tk.Button(
            button_panel,
            text="💾 Сохранить результаты",
            command=self.save_manual_test_results,
            bg="#16a085",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.btn_save_manual.pack(side=tk.RIGHT, padx=5)
        
        # Статистика ручного тестирования
        self.manual_stats_label = tk.Label(
            right_panel,
            text="Выберите тест из списка для просмотра инструкций",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Segoe UI", 9),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.manual_stats_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.update_manual_stats()
    
    # Методы для автоматических тестов
    def open_manual_guide(self):
        """Открывает руководство по ручному тестированию"""
        manual_path = os.path.join(os.path.dirname(__file__), "manual", "MANUAL_TESTING.md")
        if os.path.exists(manual_path):
            guide_window = tk.Toplevel(self.root)
            guide_window.title("Руководство по ручному тестированию")
            guide_window.geometry("800x600")
            guide_window.configure(bg="#f0f0f0")
            
            header = tk.Frame(guide_window, bg="#f39c12", height=50)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            
            title = tk.Label(
                header,
                text="Руководство по ручному тестированию IDEF0 Editor",
                font=("Segoe UI", 12, "bold"),
                bg="#f39c12",
                fg="white"
            )
            title.pack(pady=15)
            
            text_widget = scrolledtext.ScrolledText(
                guide_window,
                wrap=tk.WORD,
                font=("Segoe UI", 9),
                bg="#ffffff",
                fg="#2c3e50",
                relief=tk.SUNKEN,
                bd=1
            )
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            try:
                with open(manual_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_widget.insert(1.0, content)
                text_widget.config(state=tk.DISABLED)
            except Exception as e:
                text_widget.insert(1.0, f"Ошибка при загрузке файла: {str(e)}\n\nПуть: {manual_path}")
        else:
            messagebox.showwarning("Файл не найден", f"Файл руководства не найден:\n{manual_path}")
    
    def update_status(self, message, color="#2c3e50"):
        """Обновляет статус бар"""
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def append_output(self, text, color="#2c3e50"):
        """Добавляет текст в область вывода"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        """Очищает область вывода"""
        self.output_text.delete(1.0, tk.END)
        self.stats_label.config(text="Статистика: Запустите тесты для просмотра результатов")
        self.update_status("Готов к запуску тестов", "#2c3e50")
    
    def save_results(self):
        """Сохраняет результаты тестов в файл"""
        content = self.output_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Нет данных", "Нет результатов для сохранения. Запустите тесты сначала.")
            return
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"test_results_{timestamp}.txt"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            initialfile=default_filename
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Успех", f"Результаты сохранены в файл:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def run_tests(self, test_type):
        """Запускает тесты в отдельном потоке"""
        if self.is_running:
            messagebox.showwarning("Тесты уже выполняются", "Дождитесь завершения текущих тестов")
            return
        
        self.is_running = True
        self.progress.start(10)
        self.clear_output()
        
        thread = threading.Thread(target=self._run_tests_thread, args=(test_type,))
        thread.daemon = True
        thread.start()
    
    def _run_tests_thread(self, test_type):
        """Запускает тесты в отдельном потоке"""
        try:
            test_types = []
            if test_type == "all":
                test_types = ["unit", "integration", "automated"]
            else:
                test_types = [test_type]
            
            results = []
            total_tests = 0
            total_passed = 0
            total_failed = 0
            
            for ttype in test_types:
                self.update_status(f"Запуск {self.get_test_name(ttype)}...", "#3498db")
                
                result = self._run_test_suite(ttype)
                output = getattr(result, 'output', '')
                
                success = result.wasSuccessful()
                tests_run = result.testsRun
                failures = len(result.failures)
                errors_count = len(result.errors)
                
                total_tests += tests_run
                total_passed += tests_run - failures - errors_count
                total_failed += failures + errors_count
                
                results.append({
                    "type": ttype,
                    "success": success,
                    "tests_run": tests_run,
                    "failures": failures,
                    "errors": errors_count,
                    "output": output
                })
                
                self.append_output(f"\n{'='*70}\n")
                self.append_output(f"РЕЗУЛЬТАТЫ: {self.get_test_name(ttype)}\n")
                self.append_output(f"{'='*70}\n\n")
                self.append_output(output)
                
                if result.failures:
                    self.append_output(f"\nПРОВАЛЕННЫЕ ТЕСТЫ ({len(result.failures)}):\n", "#e74c3c")
                    for test, traceback_text in result.failures:
                        self.append_output(f"  ✗ {test}\n", "#e74c3c")
                        self.append_output(f"{traceback_text}\n", "#e74c3c")
                
                if result.errors:
                    self.append_output(f"\nОШИБКИ ({len(result.errors)}):\n", "#e74c3c")
                    for test, traceback_text in result.errors:
                        self.append_output(f"  ✗ {test}\n", "#e74c3c")
                        self.append_output(f"{traceback_text}\n", "#e74c3c")
                
                if success:
                    self.append_output(f"\n✓ {self.get_test_name(ttype)} пройдены успешно! ({tests_run} тестов)\n\n", "#27ae60")
                else:
                    self.append_output(f"\n✗ {self.get_test_name(ttype)} провалены! ({failures + errors_count} из {tests_run})\n\n", "#e74c3c")
            
            self.append_output(f"\n{'='*70}\n")
            self.append_output("ИТОГОВАЯ СТАТИСТИКА\n")
            self.append_output(f"{'='*70}\n")
            self.append_output(f"Всего тестов: {total_tests}\n")
            self.append_output(f"Пройдено: {total_passed}\n", "#27ae60")
            self.append_output(f"Провалено: {total_failed}\n", "#e74c3c")
            self.append_output(f"{'='*70}\n")
            
            if total_failed == 0:
                self.update_status(f"✓ Все тесты пройдены успешно! ({total_tests} тестов)", "#27ae60")
            else:
                self.update_status(f"✗ Провалено {total_failed} из {total_tests} тестов", "#e74c3c")
            
            stats_text = f"Всего тестов: {total_tests} | Пройдено: {total_passed} | Провалено: {total_failed}"
            self.stats_label.config(text=stats_text)
            
        except Exception as e:
            error_traceback = traceback.format_exc()
            self.append_output(f"\nОШИБКА ПРИ ЗАПУСКЕ ТЕСТОВ:\n", "#e74c3c")
            self.append_output(f"{str(e)}\n\n", "#e74c3c")
            self.append_output(f"Детали ошибки:\n{error_traceback}\n", "#e74c3c")
            self.update_status(f"Ошибка при запуске тестов: {str(e)}", "#e74c3c")
        finally:
            self.is_running = False
            self.progress.stop()
    
    def _run_test_suite(self, test_type):
        """Запускает набор тестов"""
        try:
            loader = unittest.TestLoader()
            test_dir = os.path.join(os.path.dirname(__file__), test_type)
            
            if not os.path.exists(test_dir):
                raise FileNotFoundError(f"Директория тестов не найдена: {test_dir}")
            
            top_level_dir = os.path.dirname(os.path.dirname(__file__))
            
            if top_level_dir not in sys.path:
                sys.path.insert(0, top_level_dir)
            
            suite = loader.discover(test_dir, pattern='test_*.py', top_level_dir=top_level_dir)
            
            if suite.countTestCases() == 0:
                class EmptyResult:
                    def __init__(self):
                        self.wasSuccessful = lambda: True
                        self.testsRun = 0
                        self.failures = []
                        self.errors = []
                        self.output = f"Тесты не найдены в директории: {test_dir}\n"
                return EmptyResult()
            
            stream = io.StringIO()
            runner = unittest.TextTestRunner(verbosity=2, stream=stream)
            result = runner.run(suite)
            result.output = stream.getvalue()
            
            return result
        except Exception as e:
            class ErrorResult:
                def __init__(self, error_msg, error_traceback):
                    self.wasSuccessful = lambda: False
                    self.testsRun = 0
                    self.failures = []
                    self.errors = [(test_type, error_traceback)]
                    self.output = f"Ошибка при загрузке тестов:\n{error_msg}\n\n{error_traceback}\n"
            return ErrorResult(str(e), traceback.format_exc())
    
    def get_test_name(self, test_type):
        """Возвращает название типа тестов"""
        names = {
            "unit": "Unit тесты",
            "integration": "Интеграционные тесты",
            "automated": "Автоматические UI тесты"
        }
        return names.get(test_type, test_type)
    
    # Методы для ручного тестирования
    def on_test_select(self, event):
        """Обработчик выбора теста из списка"""
        selection = self.test_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.manual_tests):
            test = self.manual_tests[index]
            self.current_test_id = test['id']
            self.show_test_instructions(test)
            
            self.btn_pass.config(state=tk.NORMAL)
            self.btn_fail.config(state=tk.NORMAL)
            self.btn_reset.config(state=tk.NORMAL)
    
    def show_test_instructions(self, test):
        """Показывает инструкции для выбранного теста"""
        self.instruction_text.config(state=tk.NORMAL)
        self.instruction_text.delete(1.0, tk.END)
        
        content = f"Тест: {test['title']}\n"
        content += f"Раздел: {test['section_title']}\n"
        content += "=" * 70 + "\n\n"
        
        if test['steps']:
            content += "ШАГИ:\n"
            content += "-" * 70 + "\n"
            for i, step in enumerate(test['steps'], 1):
                content += f"{i}. {step}\n"
            content += "\n"
        
        if test['expected']:
            content += "ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:\n"
            content += "-" * 70 + "\n"
            for expected in test['expected']:
                content += f"• {expected}\n"
            content += "\n"
        
        status = self.manual_test_results.get(test['id'], None)
        if status == "passed":
            content += "\n✓ Статус: ТЕСТ ПРОЙДЕН\n"
        elif status == "failed":
            content += "\n✗ Статус: ТЕСТ ПРОВАЛЕН\n"
        else:
            content += "\n○ Статус: НЕ ПРОТЕСТИРОВАН\n"
        
        self.instruction_text.insert(1.0, content)
        self.instruction_text.config(state=tk.DISABLED)
    
    def mark_test_result(self, result):
        """Отмечает результат теста"""
        if not self.current_test_id:
            return
        
        if result is None:
            self.manual_test_results.pop(self.current_test_id, None)
        else:
            self.manual_test_results[self.current_test_id] = result
        
        self.refresh_test_list()
        
        test = self.manual_test_parser.get_test_by_id(self.current_test_id) if self.manual_test_parser else None
        if test:
            self.show_test_instructions(test)
        
        self.update_manual_stats()
    
    def refresh_test_list(self):
        """Обновляет список тестов с учетом результатов"""
        self.test_listbox.delete(0, tk.END)
        
        for test in self.manual_tests:
            test_id = test['id']
            status = self.manual_test_results.get(test_id, None)
            prefix = "✓ " if status == "passed" else "✗ " if status == "failed" else "○ "
            color = "#27ae60" if status == "passed" else "#e74c3c" if status == "failed" else "#2c3e50"
            self.test_listbox.insert(tk.END, f"{prefix}{test['title']}")
            self.test_listbox.itemconfig(self.test_listbox.size() - 1, {'fg': color})
    
    def update_manual_stats(self):
        """Обновляет статистику ручного тестирования"""
        total = len(self.manual_tests)
        passed = sum(1 for status in self.manual_test_results.values() if status == "passed")
        failed = sum(1 for status in self.manual_test_results.values() if status == "failed")
        not_tested = total - passed - failed
        
        stats_text = f"Всего тестов: {total} | Пройдено: {passed} | Провалено: {failed} | Не протестировано: {not_tested}"
        self.manual_stats_label.config(text=stats_text)
    
    def load_manual_test_results(self):
        """Загружает сохраненные результаты ручного тестирования"""
        results_file = os.path.join(os.path.dirname(__file__), "manual_test_results.json")
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    self.manual_test_results = json.load(f)
            except Exception as e:
                print(f"Ошибка при загрузке результатов: {e}")
                self.manual_test_results = {}
        else:
            self.manual_test_results = {}
    
    def save_manual_test_results(self):
        """Сохраняет результаты ручного тестирования"""
        results_file = os.path.join(os.path.dirname(__file__), "manual_test_results.json")
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.manual_test_results, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Результаты сохранены в файл:\n{results_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить результаты:\n{str(e)}")


def main():
    """Главная функция"""
    try:
        root = tk.Tk()
        app = TestRunnerApp(root)
        root.mainloop()
    except Exception as e:
        print("Ошибка при запуске приложения:")
        print(traceback.format_exc())
        try:
            messagebox.showerror("Ошибка запуска", f"Не удалось запустить приложение:\n{str(e)}\n\nПроверьте консоль для деталей.")
        except:
            pass
        sys.exit(1)


if __name__ == '__main__':
    main()

