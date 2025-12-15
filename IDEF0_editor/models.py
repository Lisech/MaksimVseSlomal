"""
Модели данных
"""

import math
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
                 x1=None, y1=None, x2=None, y2=None, text="",
                 route_locked=False, locked_path=None):
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
        
        # Замороженный авто-маршрут (автоматические "колена")
        # Если включено, отрисовка использует сохранённый путь, лишь подтягивая начало/конец.
        self.route_locked = route_locked
        # Храним как список списков [[x,y], ...] (JSON-friendly)
        self.locked_path = locked_path
    
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
            "text": self.text,
            "route_locked": self.route_locked,
            "locked_path": self.locked_path
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
        self.route_locked = data.get("route_locked", self.route_locked)
        self.locked_path = data.get("locked_path", self.locked_path)
    
    def calculate_routing_path(self, from_block, to_block, all_blocks):
        """
        Вычисляет путь обхода блоков для стрелки с поворотами на 90 градусов
        
        Args:
            from_block: Объект Block или None (начальный блок)
            to_block: Объект Block или None (конечный блок)
            all_blocks: Список всех блоков для проверки пересечений
            
        Returns:
            list: Список точек [(x1, y1), (x2, y2), ...] для отрисовки пути
        """
        def _dedupe_consecutive(points):
            """Удаляет подряд идущие одинаковые точки, сохраняя порядок."""
            if not points:
                return points
            cleaned = [points[0]]
            for p in points[1:]:
                if p != cleaned[-1]:
                    cleaned.append(p)
            return cleaned
        
        def _segment_intersects_block(p1, p2, block):
            """Проверка пересечения сегмента с блоком через существующий детектор."""
            return self._line_intersects_block(p1[0], p1[1], p2[0], p2[1], block)
        
        def _refine_path_to_avoid_blocks(path, blocks, excluded_ids, max_iters=25):
            """
            Итеративно очищает путь: если какой-то сегмент пересекает блок, вставляет локальный обход.
            Это делает роутинг устойчивым, когда первичный обход создаёт новые пересечения.
            """
            path = _dedupe_consecutive(path)
            if len(path) < 2:
                return path
            
            # Чтобы не зациклиться на одинаковых преобразованиях
            seen = set()
            
            for _ in range(max_iters):
                changed = False
                # Проходим сегменты слева направо и чиним первое найденное пересечение
                for seg_idx in range(len(path) - 1):
                    p1 = path[seg_idx]
                    p2 = path[seg_idx + 1]
                    # Сегмент нулевой длины неинтересен
                    if p1 == p2:
                        continue
                    
                    for block in blocks:
                        if block.id in excluded_ids:
                            continue
                        if not _segment_intersects_block(p1, p2, block):
                            continue
                        
                        key = (seg_idx, p1, p2, block.id)
                        if key in seen:
                            # Мы уже пытались чинить этот же кейс — пропускаем, чтобы не зациклиться
                            continue
                        seen.add(key)
                        
                        detour = self._route_around_block(p1[0], p1[1], p2[0], p2[1], block)
                        detour = _dedupe_consecutive(detour)
                        
                        # Если обход не дал эффекта — дальше пробуем другие блоки/сегменты
                        if not detour or detour == [p1, p2]:
                            continue
                        
                        # Заменяем сегмент (p1 -> p2) на detour (он уже включает p1 и p2)
                        path = path[:seg_idx] + detour + path[seg_idx + 2:]
                        path = _dedupe_consecutive(path)
                        changed = True
                        break
                    if changed:
                        break
                
                if not changed:
                    break
            
            return path
        
        def _calculate_path_between_points(px1, py1, px2, py2, blocks, excluded_ids):
            """
            Строит ортогональный путь с обходом блоков между двумя точками.
            Это базовый строитель как для обычной стрелки, так и для стрелки с bend (waypoint).
            """
            if px1 is None or py1 is None or px2 is None or py2 is None:
                return [(px1, py1), (px2, py2)]
            
            # 1) Находим блоки, которые пересекает прямая, и строим обход ближайших
            blocking_blocks = []
            for block in blocks:
                if block.id in excluded_ids:
                    continue
                if self._line_intersects_block(px1, py1, px2, py2, block):
                    blocking_blocks.append(block)
            
            # 1.1) Агрессивная проверка (оставляем старую логику, только на параметрах)
            if not blocking_blocks:
                for block in blocks:
                    if block.id in excluded_ids:
                        continue
                    
                    block_left = block.x - block.width / 2
                    block_right = block.x + block.width / 2
                    block_top = block.y - block.height / 2
                    block_bottom = block.y + block.height / 2
                    
                    margin = max(block.width, block.height) / 2
                    min_x = min(px1, px2) - margin
                    max_x = max(px1, px2) + margin
                    min_y = min(py1, py2) - margin
                    max_y = max(py1, py2) + margin
                    
                    if not (block_right < min_x or block_left > max_x or block_bottom < min_y or block_top > max_y):
                        if self._line_intersects_block(px1, py1, px2, py2, block):
                            blocking_blocks.append(block)
                        else:
                            # Доп. проверка через ближайшую точку к центру
                            block_center_x = block.x
                            block_center_y = block.y
                            dx = px2 - px1
                            dy = py2 - py1
                            length_sq = dx * dx + dy * dy
                            if length_sq > 0.001:
                                t = max(0, min(1, ((block_center_x - px1) * dx + (block_center_y - py1) * dy) / length_sq))
                                nearest_x = px1 + t * dx
                                nearest_y = py1 + t * dy
                                if (block_left < nearest_x < block_right and block_top < nearest_y < block_bottom):
                                    blocking_blocks.append(block)
            
            if not blocking_blocks:
                return [(px1, py1), (px2, py2)]
            
            def block_distance(block):
                block_left = block.x - block.width / 2
                block_right = block.x + block.width / 2
                block_top = block.y - block.height / 2
                block_bottom = block.y + block.height / 2
                closest_x = max(block_left, min(px1, block_right))
                closest_y = max(block_top, min(py1, block_bottom))
                dx = closest_x - px1
                dy = closest_y - py1
                return math.sqrt(dx * dx + dy * dy)
            
            blocking_blocks.sort(key=block_distance)
            
            path = [(px1, py1)]
            current_x, current_y = px1, py1
            target_x, target_y = px2, py2
            
            for block in blocking_blocks:
                path_segment = self._route_around_block(
                    current_x, current_y, target_x, target_y, block
                )
                if len(path_segment) > 1:
                    path.extend(path_segment[1:])
                    current_x, current_y = path_segment[-1]
            
            # 2) Второй проход: дочищаем путь от вторичных пересечений
            path = _refine_path_to_avoid_blocks(path, blocks, excluded_ids)
            return path
        
        # Сначала вычисляем начальную и конечную точки
        if from_block:
            x1, y1 = self._get_side_point(
                from_block, self.from_side, self.from_attachment_point
            )
        else:
            x1, y1 = self.x1, self.y1
        
        if to_block:
            x2, y2 = self._get_side_point(
                to_block, self.to_side, self.to_attachment_point
            )
        else:
            x2, y2 = self.x2, self.y2
        
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return [(x1, y1), (x2, y2)]
        
        # Какие блоки считаем "своими" и не обходим ими же самими
        excluded_ids = set()
        if self.from_block_id:
            excluded_ids.add(self.from_block_id)
        if self.to_block_id:
            excluded_ids.add(self.to_block_id)
        
        # Если задан bend (waypoint), строим путь в 2 этапа: start->bend и bend->end.
        # Это гарантирует, что пользовательский изгиб НЕ сбрасывается при прикреплении.
        bx, by = self.bend_x, self.bend_y
        if bx is not None and by is not None:
            # Защита от вырожденных случаев, чтобы не "ломать" путь, если bend совпал с концом
            if (abs(bx - x1) + abs(by - y1) < 0.5) or (abs(bx - x2) + abs(by - y2) < 0.5):
                bx = by = None
        
        if bx is not None and by is not None:
            p1 = _calculate_path_between_points(x1, y1, bx, by, all_blocks, excluded_ids)
            p2 = _calculate_path_between_points(bx, by, x2, y2, all_blocks, excluded_ids)
            if p2 and p1 and len(p2) > 0:
                # Склеиваем без дублирования bend-точки
                merged = p1 + p2[1:]
            else:
                merged = p1 or p2
            merged = _dedupe_consecutive(merged)
            return merged
        
        return _calculate_path_between_points(x1, y1, x2, y2, all_blocks, excluded_ids)
    
    def _line_intersects_block(self, x1, y1, x2, y2, block):
        """
        Проверяет, пересекает ли прямая линия внутреннюю область блока
        
        Args:
            x1, y1: Начальная точка линии
            x2, y2: Конечная точка линии
            block: Объект Block
            
        Returns:
            bool: True если линия пересекает внутреннюю область блока
        """
        # Границы блока + небольшой допуск, чтобы учитывать касание границы
        eps = 0.5
        block_left = block.x - block.width / 2 - eps
        block_right = block.x + block.width / 2 + eps
        block_top = block.y - block.height / 2 - eps
        block_bottom = block.y + block.height / 2 + eps
        
        # Проверяем, находится ли хотя бы одна точка внутри или на границе блока
        if (block_left <= x1 <= block_right and block_top <= y1 <= block_bottom):
            return True
        if (block_left <= x2 <= block_right and block_top <= y2 <= block_bottom):
            return True
        
        # Используем алгоритм проверки пересечения отрезка с прямоугольником
        dx = x2 - x1
        dy = y2 - y1
        
        # Если линия очень короткая
        if abs(dx) < 0.001 and abs(dy) < 0.001:
            return False
        
        # Нормализуем направление линии
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.001:
            return False
        
        # Более агрессивная проверка: проверяем много точек на линии
        num_samples = max(50, int(length * 2))  # Две точки на каждый пиксель (минимум 50 точек)

        # Проверяем точки на линии, исключая сами концы (которые могут быть на границе)
        for i in range(1, num_samples):
            t = i / num_samples
            test_x = x1 + t * dx
            test_y = y1 + t * dy
            
            # Проверяем, находится ли эта точка внутри или на границе блока
            if (block_left <= test_x <= block_right and block_top <= test_y <= block_bottom):
                return True
        
        # Дополнительная проверка: используем алгоритм пересечения отрезка с прямоугольником
        # Находим все точки пересечения со сторонами блока
        intersections = []
        
        # Верхняя сторона (y = block_top)
        if abs(dy) > 0.001:
            t = (block_top - y1) / dy
            if 0 < t < 1:  # Пересечение внутри отрезка (не на концах)
                x = x1 + t * dx
                if block_left <= x <= block_right:
                    intersections.append((x, block_top, t))
        
        # Нижняя сторона (y = block_bottom)
        if abs(dy) > 0.001:
            t = (block_bottom - y1) / dy
            if 0 < t < 1:
                x = x1 + t * dx
                if block_left <= x <= block_right:
                    intersections.append((x, block_bottom, t))
        
        # Левая сторона (x = block_left)
        if abs(dx) > 0.001:
            t = (block_left - x1) / dx
            if 0 < t < 1:
                y = y1 + t * dy
                if block_top <= y <= block_bottom:
                    intersections.append((block_left, y, t))
        
        # Правая сторона (x = block_right)
        if abs(dx) > 0.001:
            t = (block_right - x1) / dx
            if 0 < t < 1:
                y = y1 + t * dy
                if block_top <= y <= block_bottom:
                    intersections.append((block_right, y, t))
        
        # Если есть хотя бы две точки пересечения со сторонами, проверяем среднюю точку
        if len(intersections) >= 2:
            # Сортируем по параметру t
            intersections.sort(key=lambda p: p[2])
            # Берем среднюю точку между первыми двумя пересечениями
            mid_t = (intersections[0][2] + intersections[1][2]) / 2
            mid_x = x1 + mid_t * dx
            mid_y = y1 + mid_t * dy
            # Если средняя точка внутри блока, значит линия проходит через блок
            if (block_left < mid_x < block_right and block_top < mid_y < block_bottom):
                return True
        
        # Если есть одно пересечение, проверяем точку на середине линии
        if len(intersections) == 1:
            mid_t = 0.5
            mid_x = x1 + mid_t * dx
            mid_y = y1 + mid_t * dy
            # Если средняя точка линии внутри блока, значит линия проходит через блок
            if (block_left < mid_x < block_right and block_top < mid_y < block_bottom):
                return True
        
        return False
    
    def _route_around_block(self, x1, y1, x2, y2, block):
        """
        Вычисляет путь обхода одного блока с поворотами на 90 градусов
        
        Args:
            x1, y1: Начальная точка
            x2, y2: Конечная точка
            block: Объект Block для обхода
            
        Returns:
            list: Список точек [(x1, y1), (x2, y2), ...] для обхода блока
        """
        # Границы блока с небольшим отступом
        padding = 5
        block_left = block.x - block.width / 2 - padding
        block_right = block.x + block.width / 2 + padding
        block_top = block.y - block.height / 2 - padding
        block_bottom = block.y + block.height / 2 + padding
        
        # Генерируем 4 возможных пути обхода (сверху, снизу, слева, справа)
        paths = []
        
        # Путь 1: обход сверху
        path_top = []
        # От начальной точки до верхней границы блока
        if x1 < block_left:
            path_top.append((block_left, y1))
            path_top.append((block_left, block_top))
        elif x1 > block_right:
            path_top.append((block_right, y1))
            path_top.append((block_right, block_top))
        else:
            path_top.append((x1, block_top))
        
        # По верхней границе до точки над конечной координатой
        path_top.append((x2, block_top))
        
        # От верхней границы до конечной точки
        if x2 < block_left:
            path_top.append((block_left, block_top))
            path_top.append((block_left, y2))
        elif x2 > block_right:
            path_top.append((block_right, block_top))
            path_top.append((block_right, y2))
        paths.append(("top", path_top))
        
        # Путь 2: обход снизу
        path_bottom = []
        # От начальной точки до нижней границы блока
        if x1 < block_left:
            path_bottom.append((block_left, y1))
            path_bottom.append((block_left, block_bottom))
        elif x1 > block_right:
            path_bottom.append((block_right, y1))
            path_bottom.append((block_right, block_bottom))
        else:
            path_bottom.append((x1, block_bottom))
        
        # По нижней границе до точки под конечной координатой
        path_bottom.append((x2, block_bottom))
        
        # От нижней границы до конечной точки
        if x2 < block_left:
            path_bottom.append((block_left, block_bottom))
            path_bottom.append((block_left, y2))
        elif x2 > block_right:
            path_bottom.append((block_right, block_bottom))
            path_bottom.append((block_right, y2))
        paths.append(("bottom", path_bottom))
        
        # Путь 3: обход слева
        path_left = []
        # От начальной точки до левой границы блока
        if y1 < block_top:
            path_left.append((x1, block_top))
            path_left.append((block_left, block_top))
        elif y1 > block_bottom:
            path_left.append((x1, block_bottom))
            path_left.append((block_left, block_bottom))
        else:
            path_left.append((block_left, y1))
        
        # По левой границе до точки слева от конечной координаты
        path_left.append((block_left, y2))
        
        # От левой границы до конечной точки
        if y2 < block_top:
            path_left.append((block_left, block_top))
            path_left.append((x2, block_top))
        elif y2 > block_bottom:
            path_left.append((block_left, block_bottom))
            path_left.append((x2, block_bottom))
        paths.append(("left", path_left))
        
        # Путь 4: обход справа
        path_right = []
        # От начальной точки до правой границы блока
        if y1 < block_top:
            path_right.append((x1, block_top))
            path_right.append((block_right, block_top))
        elif y1 > block_bottom:
            path_right.append((x1, block_bottom))
            path_right.append((block_right, block_bottom))
        else:
            path_right.append((block_right, y1))
        
        # По правой границе до точки справа от конечной координаты
        path_right.append((block_right, y2))
        
        # От правой границы до конечной точки
        if y2 < block_top:
            path_right.append((block_right, block_top))
            path_right.append((x2, block_top))
        elif y2 > block_bottom:
            path_right.append((block_right, block_bottom))
            path_right.append((x2, block_bottom))
        paths.append(("right", path_right))
        
        # Выбираем самый короткий путь
        min_length = float('inf')
        best_path = None
        
        for name, path in paths:
            # Вычисляем длину пути: от (x1,y1) через path до (x2,y2)
            length = 0
            
            # От начальной точки до первой точки пути
            if len(path) > 0:
                dx = path[0][0] - x1
                dy = path[0][1] - y1
                length += math.sqrt(dx*dx + dy*dy)
            
            # Между точками пути
            for i in range(len(path) - 1):
                dx = path[i+1][0] - path[i][0]
                dy = path[i+1][1] - path[i][1]
                length += math.sqrt(dx*dx + dy*dy)
            
            # От последней точки пути до конечной точки
            if len(path) > 0:
                dx = x2 - path[-1][0]
                dy = y2 - path[-1][1]
                length += math.sqrt(dx*dx + dy*dy)
            
            if length < min_length:
                min_length = length
                best_path = path
        
        if best_path:
            # Удаляем дубликаты последовательных точек
            cleaned_path = [(x1, y1)]
            for point in best_path:
                if len(cleaned_path) == 0 or point != cleaned_path[-1]:
                    cleaned_path.append(point)
            if len(cleaned_path) == 0 or (x2, y2) != cleaned_path[-1]:
                cleaned_path.append((x2, y2))
            return cleaned_path
        else:
            return [(x1, y1), (x2, y2)]


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