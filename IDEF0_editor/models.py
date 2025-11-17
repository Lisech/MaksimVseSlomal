class Block:
    def __init__(self, block_id=None, name="Входит название...", code="A0", 
                 element_type="Выберите тип...", description="Входит основное элемента...",
                 x=150, y=150, width=150, height=50, color="#E3F2FD", border_width=2):
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
            self.current_level = 0  # Текущий уровень вложенности
            self.level_stack = []   # Стек для навигации по уровням
            self.blocks_by_level = {}  # Блоки по уровням
        
        def get_blocks_for_current_level(self, all_blocks):
            """Возвращает блоки для текущего уровня"""
            return [block for block in all_blocks if block.level == self.current_level]
        
        def get_child_blocks(self, parent_block, all_blocks):
            """Возвращает дочерние блоки для указанного родительского блока"""
            return [block for block in all_blocks if block.parent_id == parent_block.id]
        
        def enter_level(self, parent_block):
            """Переход на уровень ниже (проваливаемся в блок)"""
            if parent_block:
                self.level_stack.append(self.current_level)
                self.current_level = parent_block.level + 1
                return True
            return False
        
        def exit_level(self):
            """Возврат на уровень выше"""
            if self.level_stack:
                self.current_level = self.level_stack.pop()
                return True
            return False
        
        def get_current_parent_id(self):
            """Возвращает ID родительского блока для текущего уровня"""
            if self.level_stack:
                # Находим блок, соответствующий предыдущему уровню в стеке
                return self.level_stack[-1]
            return None
        
        def get_level_path(self, all_blocks):
            """Возвращает путь текущего уровня в виде строки"""
            if not self.level_stack:
                return "Уровень 0"
            
            path = "Уровень 0"
            current_parent = None
            
            # Строим путь через родительские блоки
            for level in self.level_stack + [self.current_level]:
                if level > 0:
                    # Находим родительский блок для этого уровня
                    parent = next((b for b in all_blocks if b.level == level - 1 and 
                                (current_parent is None or b.parent_id == getattr(current_parent, 'id', None))), None)
                    if parent:
                        path += f" → {parent.code}"
                        current_parent = parent
            
            return path