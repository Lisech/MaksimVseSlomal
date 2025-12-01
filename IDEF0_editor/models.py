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

    def to_dict_full(self):
        """Словарь для сохранения в JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "element_type": self.element_type,
            "description": self.description,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color,
            "border_width": self.border_width,
            "parent_id": self.parent_id,
            "level": self.level
        }

    def from_dict(data):
        """Создание блока из словаря JSON"""
        return Block(
            block_id=data["id"],
            name=data["name"],
            code=data["code"],
            element_type=data["element_type"],
            description=data["description"],
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            color=data["color"],
            border_width=data["border_width"],
            parent_id=data["parent_id"],
            level=data["level"]
        )
    
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
        self.current_level_path = []  # Текущий путь в виде списка block_id
        self.level_history = {}  # Состояния для каждого уровня
    
    def get_blocks_for_current_level(self, all_blocks):
        """Возвращает блоки для текущего уровня"""
        if not self.current_level_path:
            # Корневой уровень - блоки без parent_id
            return [block for block in all_blocks if block.parent_id is None]
        else:
            # Уровень детализации - блоки с parent_id = последнему в пути
            parent_id = self.current_level_path[-1]
            return [block for block in all_blocks if block.parent_id == parent_id]
    
    def enter_block_level(self, block):
        """Переход на уровень детализации блока"""
        if block:
            # Добавляем блок в путь
            self.current_level_path.append(block.id)
            return True
        return False
    
    def exit_level(self):
        """Возврат на уровень выше"""
        if self.current_level_path:
            self.current_level_path.pop()
            return True
        return False
    
    def get_current_parent_id(self):
        """Возвращает ID родительского блока для текущего уровня"""
        if self.current_level_path:
            return self.current_level_path[-1]
        return None
    
    def get_level_path(self, all_blocks):
        """Возвращает путь текущего уровня в виде строки"""
        if not self.current_level_path:
            return "Уровень 0"
        
        # Строим путь из кодов блоков
        path_parts = ["Уровень 0"]
        current_parent_id = None
        
        for block_id in self.current_level_path:
            block = next((b for b in all_blocks if b.id == block_id), None)
            if block:
                path_parts.append(block.code)
                current_parent_id = block.id
        
        return " -> ".join(path_parts)
    
    def get_current_level_name(self):
        """Возвращает имя текущего уровня"""
        if not self.current_level_path:
            return "Уровень 0"
        
        # Возвращаем код последнего блока в пути
        return f"Уровень {len(self.current_level_path)}"
    
    def save_level_state(self, level_key, state):
        """Сохраняет состояние уровня"""
        self.level_history[level_key] = state
    
    def get_level_state(self, level_key):
        """Возвращает сохраненное состояние уровня"""
        return self.level_history.get(level_key)
    
    def get_current_level_key(self):
        """Возвращает уникальный ключ для текущего уровня"""
        return "->".join(self.current_level_path) if self.current_level_path else "root"
    def build_hierarchy_tree(self, all_blocks):
        """Строит иерархическое дерево всех блоков"""
        def build_tree(parent_id=None, level=0):
            children = []
            for block in all_blocks:
                if block.parent_id == parent_id:
                    child_data = {
                        'block': block,
                        'level': level,
                        'children': build_tree(block.id, level + 1)
                    }
                    children.append(child_data)
            return children
        
        return build_tree()

    def goto_level_path(self, target_path):
        """Переход на указанный путь уровней"""
        self.current_level_path = target_path.copy()

    def save_level_state(self, level_key, state):
        """Сохраняет состояние уровня"""
        self.level_history[level_key] = state
    
    def get_level_state(self, level_key):
        """Возвращает сохраненное состояние уровня"""
        return self.level_history.get(level_key)
