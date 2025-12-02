"""
Модели данных
"""

from styles import Colors


class Block:
    def __init__(self, block_id=None, name="Входит название...", code="A0", 
                 element_type="Выберите тип...", description="Входит основное элемента...",
                 x=150, y=150, width=150, height=50, color=None, border_width=2, parent_id=None):
        self.id = block_id
        self.name = name
        self.code = code
        self.element_type = element_type
        self.description = description
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color or Colors.BLOCK_FILL
        self.border_width = border_width
        self.parent_id = parent_id  # ID родительского блока для иерархии
    
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
            "border_width": self.border_width,
            "parent_id": self.parent_id
        }
    
    def to_dict_full(self):
        """Полный словарь для сохранения (включая id)"""
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
            "parent_id": self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создает блок из словаря"""
        return cls(
            block_id=data.get("id"),
            name=data.get("name", "Входит название..."),
            code=data.get("code", "A0"),
            element_type=data.get("element_type", "Выберите тип..."),
            description=data.get("description", "Входит основное элемента..."),
            x=data.get("x", 150),
            y=data.get("y", 150),
            width=data.get("width", 150),
            height=data.get("height", 50),
            color=data.get("color"),
            border_width=data.get("border_width", 2),
            parent_id=data.get("parent_id")
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
        if "parent_id" in data:
            self.parent_id = data.get("parent_id")
    
    def get_attachment_points(self, side):
        """
        Возвращает список координат точек прикрепления на указанной стороне
        
        Args:
            side: Сторона ("left", "right", "top", "bottom")
            
        Returns:
            list: Список из 3 кортежей (x, y) - координаты точек прикрепления
        """
        points = []
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        
        if side == "left" or side == "right":
            # Вертикальная сторона - 3 точки по вертикали
            for i in range(3):
                offset = (i - 1) * (height / 3)  # -height/3, 0, height/3
                if side == "left":
                    points.append((x - width / 2, y + offset))
                else:  # right
                    points.append((x + width / 2, y + offset))
        else:  # top or bottom
            # Горизонтальная сторона - 3 точки по горизонтали
            for i in range(3):
                offset = (i - 1) * (width / 3)  # -width/3, 0, width/3
                if side == "top":
                    points.append((x + offset, y - height / 2))
                else:  # bottom
                    points.append((x + offset, y + height / 2))
        
        return points


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
                 color="#000000", width=2, style="solid",
                 x1=None, y1=None, x2=None, y2=None, text=""):
        """
        Инициализация стрелки
        
        Args:
            arrow_id: Уникальный идентификатор стрелки
            from_block_id: ID блока, от которого начинается стрелка (None если свободная точка)
            to_block_id: ID блока, к которому ведет стрелка (None если свободная точка)
            from_side: Сторона начального блока ("left", "right", "top", "bottom")
            to_side: Сторона конечного блока ("left", "right", "top", "bottom")
            color: Цвет стрелки (по умолчанию черный)
            width: Толщина линии стрелки
            style: Стиль линии ("solid", "dashed", "dotted")
            x1, y1: Координаты начальной точки (если from_block_id == None)
            x2, y2: Координаты конечной точки (если to_block_id == None)
            text: Текст на стрелке
        """
        self.id = arrow_id
        self.from_block_id = from_block_id  # ID начального блока
        self.to_block_id = to_block_id      # ID конечного блока
        
        # Стороны соединения
        self.from_side = from_side  # "left", "right", "top", "bottom"
        self.to_side = to_side
        
        # Точки прикрепления (0, 1, 2 - индекс точки на стороне)
        self.from_attachment_point = None  # индекс точки прикрепления на начальной стороне
        self.to_attachment_point = None    # индекс точки прикрепления на конечной стороне
        
        # Визуальные свойства
        self.color = color
        self.width = width
        self.style = style
        self.text = text  # Текст на стрелке
        
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
        
        # Точка изгиба стрелки (None если стрелка прямая)
        self.bend_x = None
        self.bend_y = None
    
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
                from_block, self.from_side, self.from_attachment_point
            )
        else:
            # Используем свободные координаты
            self.display_x1 = self.x1
            self.display_y1 = self.y1
        
        # Вычисляем конечную точку
        if to_block:
            self.display_x2, self.display_y2 = self._get_side_point(
                to_block, self.to_side, self.to_attachment_point
            )
        else:
            # Используем свободные координаты
            self.display_x2 = self.x2
            self.display_y2 = self.y2
    
    def _get_side_point(self, block, side, attachment_point=None):
        """
        Получает точку на стороне блока
        
        Args:
            block: Объект Block
            side: Сторона ("left", "right", "top", "bottom")
            attachment_point: Индекс точки прикрепления (0, 1, 2) или None для центра
            
        Returns:
            tuple: (x, y) координаты точки
        """
        x = block.x
        y = block.y
        width = block.width
        height = block.height
        
        # Если указана точка прикрепления, используем её
        if attachment_point is not None:
            return self._get_attachment_point(block, side, attachment_point)
        
        # Иначе возвращаем центр стороны (старое поведение)
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
    
    def _get_attachment_point(self, block, side, point_index):
        """
        Получает координаты точки прикрепления на стороне блока
        
        Args:
            block: Объект Block
            side: Сторона ("left", "right", "top", "bottom")
            point_index: Индекс точки (0, 1, 2) - верхняя/левая, средняя, нижняя/правая
            
        Returns:
            tuple: (x, y) координаты точки
        """
        x = block.x
        y = block.y
        width = block.width
        height = block.height
        
        # Вычисляем позицию точки на стороне (0 = начало, 1 = середина, 2 = конец)
        if side == "left" or side == "right":
            # Вертикальная сторона
            offset = (point_index - 1) * (height / 3)  # -height/3, 0, height/3
            if side == "left":
                return (x - width / 2, y + offset)
            else:  # right
                return (x + width / 2, y + offset)
        else:  # top or bottom
            # Горизонтальная сторона
            offset = (point_index - 1) * (width / 3)  # -width/3, 0, width/3
            if side == "top":
                return (x + offset, y - height / 2)
            else:  # bottom
                return (x + offset, y + height / 2)
    
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
            self.from_attachment_point = None
        
        if self.to_block_id == block_id:
            # Сохраняем текущие координаты перед отключением
            if self.display_x2 is not None and self.display_y2 is not None:
                self.x2 = self.display_x2
                self.y2 = self.display_y2
            self.to_block_id = None
            self.to_side = None
            self.to_attachment_point = None
    
    def connect_to_block(self, block_id, side, is_start=True, attachment_point=None):
        """
        Подключает стрелку к блоку
        
        Args:
            block_id: ID блока
            side: Сторона блока ("left", "right", "top", "bottom")
            is_start: True для начальной точки, False для конечной
            attachment_point: Индекс точки прикрепления (0, 1, 2) или None
        """
        if is_start:
            self.from_block_id = block_id
            self.from_side = side
            self.from_attachment_point = attachment_point
            self.x1 = None
            self.y1 = None
        else:
            self.to_block_id = block_id
            self.to_side = side
            self.to_attachment_point = attachment_point
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
            "from_attachment_point": self.from_attachment_point,
            "to_attachment_point": self.to_attachment_point,
            "color": self.color,
            "width": self.width,
            "style": self.style,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "bend_x": self.bend_x,
            "bend_y": self.bend_y,
            "text": self.text
        }
    
    def update_from_dict(self, data):
        """Обновляет свойства стрелки из словаря"""
        self.from_block_id = data.get("from_block_id", self.from_block_id)
        self.to_block_id = data.get("to_block_id", self.to_block_id)
        self.from_side = data.get("from_side", self.from_side)
        self.to_side = data.get("to_side", self.to_side)
        self.from_attachment_point = data.get("from_attachment_point", self.from_attachment_point)
        self.to_attachment_point = data.get("to_attachment_point", self.to_attachment_point)
        self.color = data.get("color", self.color)
        self.width = data.get("width", self.width)
        self.style = data.get("style", self.style)
        self.x1 = data.get("x1", self.x1)
        self.y1 = data.get("y1", self.y1)
        self.x2 = data.get("x2", self.x2)
        self.y2 = data.get("y2", self.y2)
        self.bend_x = data.get("bend_x", self.bend_x)
        self.bend_y = data.get("bend_y", self.bend_y)
        self.text = data.get("text", self.text if hasattr(self, 'text') else "")


class LayerManager:
    """Менеджер слоев для работы с иерархией блоков"""
    
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
        for block_id in self.current_level_path:
            block = next((b for b in all_blocks if b.id == block_id), None)
            if block:
                path_parts.append(block.code)
        
        return " -> ".join(path_parts)
    
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