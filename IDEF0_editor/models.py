"""
Модели данных
"""

class Block:
    def __init__(self, block_id=None, name="Входит название...", code="A0", 
                 element_type="Выберите тип...", description="Входит основное элемента...",
                 x=150, y=150, width=150, height=50, color="#E3F2FD"):
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
            "color": self.color
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