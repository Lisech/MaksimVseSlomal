

class Block:
    def __init__(self, block_id, x=150, y=150, width=150, height=80):
        self.id = block_id
        self.name = f"Блок {block_id}"
        self.code = f"A{block_id}"
        self.element_type = "Активность"
        self.description = "Описание блока..."
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = "#E3F2FD"
        self.canvas_ids = []  # ID элементов на холсте