from styles import Colors

class Block:
    def __init__(self, block_id=None, name="Входит название...", code="A0", 
                 description="Входит основное элемента...",
                 x=150, y=150, width=150, height=50, color=None, border_width=2, parent_id=None, level=0):
        self.id = block_id
        self.name = name
        self.code = code
        self.description = description
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color or Colors.BLOCK_FILL
        self.border_width = border_width
        self.parent_id = parent_id
        self.level = level
    
    def to_dict(self):
        """Преобразует блок в словарь для отображения в свойствах"""
        return {
            "name": self.name,
            "code": self.code,
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


class Arrow:
    """
    Модель стрелки, которая может соединяться с фигурами
    
    Стрелка имеет:
    - Начальную точку соединения (from_block_id, from_side)
    - Конечную точку соединения (to_block_id, to_side)
    - Визуальные свойства (цвет, толщина, стиль)
    """
    
    def __init__(self, arrow_id=None, 
                 from_block_id=None, to_block_id=None,
                 from_side="right", to_side="left",
                 color=None, width=2, style="solid",
                 x1=None, y1=None, x2=None, y2=None):
        """
        Инициализация стрелки
        
        Args:
            arrow_id: Уникальный идентификатор стрелки
            from_block_id: ID блока, от которого начинается стрелка (None если свободная точка)
            to_block_id: ID блока, к которому ведет стрелка (None если свободная точка)
            from_side: Сторона начального блока ("left", "right", "top", "bottom")
            to_side: Сторона конечного блока ("left", "right", "top", "bottom")
            color: Цвет стрелки (по умолчанию из темы)
            width: Толщина линии стрелки
            style: Стиль линии ("solid", "dashed", "dotted")
            x1, y1: Координаты начальной точки (если from_block_id == None)
            x2, y2: Координаты конечной точки (если to_block_id == None)
        """
        self.id = arrow_id
        self.from_block_id = from_block_id  # ID начального блока
        self.to_block_id = to_block_id      # ID конечного блока
        
        # Стороны соединения
        self.from_side = from_side  # "left", "right", "top", "bottom"
        self.to_side = to_side
        
        # Визуальные свойства
        self.color = color or Colors.ARROW_COLOR
        self.width = width
        self.style = style
        
        # Свободные координаты (если стрелка не привязана к блоку)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
        # Координаты для отображения (вычисляются динамически)
        self.display_x1 = None
        self.display_y1 = None
        self.display_x2 = None
        self.display_y2 = None
    
    def calculate_connection_points(self, from_block, to_block):
        """
        Вычисляет точки соединения на основе блоков и их сторон
        
        Args:
            from_block: Объект Block или None
            to_block: Объект Block или None
        """
        # Вычисляем начальную точку
        if from_block:
            self.display_x1, self.display_y1 = self._get_side_point(
                from_block, self.from_side
            )
        else:
            # Используем свободные координаты
            self.display_x1 = self.x1
            self.display_y1 = self.y1
        
        # Вычисляем конечную точку
        if to_block:
            self.display_x2, self.display_y2 = self._get_side_point(
                to_block, self.to_side
            )
        else:
            # Используем свободные координаты
            self.display_x2 = self.x2
            self.display_y2 = self.y2
    
    def _get_side_point(self, block, side):
        """
        Получает точку на стороне блока
        
        Args:
            block: Объект Block
            side: Сторона ("left", "right", "top", "bottom")
            
        Returns:
            tuple: (x, y) координаты точки
        """
        x = block.x
        y = block.y
        width = block.width
        height = block.height
        
        if side == "left":
            return (x - width / 2, y)
        elif side == "right":
            return (x + width / 2, y)
        elif side == "top":
            return (x, y - height / 2)
        elif side == "bottom":
            return (x, y + height / 2)
        else:
            # По умолчанию возвращаем центр блока
            return (x, y)
    
    def is_connected_to_block(self, block_id):
        """Проверяет, соединена ли стрелка с указанным блоком"""
        return self.from_block_id == block_id or self.to_block_id == block_id
    
    def get_connected_block_ids(self):
        """Возвращает список ID всех блоков, к которым подключена стрелка"""
        ids = []
        if self.from_block_id:
            ids.append(self.from_block_id)
        if self.to_block_id:
            ids.append(self.to_block_id)
        return ids
    
    def disconnect_from_block(self, block_id):
        """
        Отключает стрелку от блока, сохраняя текущие координаты
        
        Args:
            block_id: ID блока, от которого нужно отключиться
        """
        if self.from_block_id == block_id:
            # Сохраняем текущие координаты перед отключением
            if self.display_x1 is not None and self.display_y1 is not None:
                self.x1 = self.display_x1
                self.y1 = self.display_y1
            self.from_block_id = None
            self.from_side = None
        
        if self.to_block_id == block_id:
            # Сохраняем текущие координаты перед отключением
            if self.display_x2 is not None and self.display_y2 is not None:
                self.x2 = self.display_x2
                self.y2 = self.display_y2
            self.to_block_id = None
            self.to_side = None
    
    def connect_to_block(self, block_id, side, is_start=True):
        """
        Подключает стрелку к блоку
        
        Args:
            block_id: ID блока
            side: Сторона блока ("left", "right", "top", "bottom")
            is_start: True для начальной точки, False для конечной
        """
        if is_start:
            self.from_block_id = block_id
            self.from_side = side
            self.x1 = None
            self.y1 = None
        else:
            self.to_block_id = block_id
            self.to_side = side
            self.x2 = None
            self.y2 = None
    
    def to_dict(self):
        """Преобразует стрелку в словарь для сохранения/отображения"""
        return {
            "id": self.id,
            "from_block_id": self.from_block_id,
            "to_block_id": self.to_block_id,
            "from_side": self.from_side,
            "to_side": self.to_side,
            "color": self.color,
            "width": self.width,
            "style": self.style,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2
        }
    
    def update_from_dict(self, data):
        """Обновляет свойства стрелки из словаря"""
        self.from_block_id = data.get("from_block_id", self.from_block_id)
        self.to_block_id = data.get("to_block_id", self.to_block_id)
        self.from_side = data.get("from_side", self.from_side)
        self.to_side = data.get("to_side", self.to_side)
        self.color = data.get("color", self.color)
        self.width = data.get("width", self.width)
        self.style = data.get("style", self.style)
        self.x1 = data.get("x1", self.x1)
        self.y1 = data.get("y1", self.y1)
        self.x2 = data.get("x2", self.x2)
        self.y2 = data.get("y2", self.y2)


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