class Block:
    def __init__(self, block_id=None, name="Входит название...", code="A0", 
                 element_type="Выберите тип...", description="Входит основное элемента...",
                 x=150, y=150, width=150, height=50, color="#E3F2FD", border_width=2, parent_id=None, level=0):
        self.id = block_id
        self.name = name
        self.code = code
        self.element_type = element_type
        self.description = description
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.border_width = border_width
        self.parent_id = parent_id
        self.level = level
    
    def to_dict(self):
        """Преобразует блок в словарь для отображения в свойствах"""
        return {
            "name": self.name,
            "code": self.code,
            "element_type": self.element_type,
            "description": self.description,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color,
            "border_width": self.border_width
        }
    
    def update_from_dict(self, data):
        """Обновляет свойства блока из словаря"""
        self.name = data.get("name", self.name)
        self.code = data.get("code", self.code)
        self.element_type = data.get("element_type", self.element_type)
        self.description = data.get("description", self.description)
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.width = data.get("width", self.width)
        self.height = data.get("height", self.height)
        self.color = data.get("color", self.color)
        self.border_width = data.get("border_width", self.border_width)
    
    def get_code_position(self):
        """Возвращает позицию для отображения кода (правый нижний угол)"""
        return (
            self.x + self.width / 2 - 10,  # x - смещение от правого края
            self.y + self.height / 2 - 10  # y - смещение от нижнего края
        )

class LayerManager:
    """Менеджер слоев для работы с вложенностью блоков"""
    
    def __init__(self):
        self.current_level = 0
        self.level_stack = []  # Стек для хранения истории переходов
    
    def get_blocks_for_current_level(self, all_blocks):
        """Возвращает блоки для текущего уровня"""
        return [block for block in all_blocks if block.level == self.current_level]
    
    def enter_block_level(self, block):
        """Переход на уровень блока (проваливаемся в блок)"""
        if block:
            # Сохраняем текущий уровень и ID блока в стек
            self.level_stack.append({
                'level': self.current_level,
                'block_id': block.id,
                'block_code': block.code
            })
            # Устанавливаем уровень равным коду блока (просто меняем current_level)
            self.current_level = block.level + 1
            return True
        return False
    
    def exit_level(self):
        """Возврат на уровень выше"""
        if self.level_stack:
            previous_level = self.level_stack.pop()
            self.current_level = previous_level['level']
            return True
        return False
    
    def get_current_parent_id(self):
        """Возвращает ID родительского блока для текущего уровня"""
        if self.level_stack:
            return self.level_stack[-1]['block_id']
        return None
    
    def get_level_path(self, all_blocks):
        """Возвращает путь текущего уровня в виде строки"""
        if not self.level_stack:
            return "Уровень 0"
        
        # Строим путь из кодов блоков в стеке
        path_parts = ["Уровень 0"]
        for stack_item in self.level_stack:
            path_parts.append(stack_item['block_code'])
        
        return " -> ".join(path_parts)
    
    def get_current_level_name(self):
        """Возвращает имя текущего уровня"""
        if self.level_stack:
            return self.level_stack[-1]['block_code']
        return "Уровень 0"