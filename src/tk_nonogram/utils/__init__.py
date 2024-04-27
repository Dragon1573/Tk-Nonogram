class Activity:
    """单元格操作事件"""

    def __init__(self, x: int, y: int, is_context: bool) -> None:
        """
        Args:
            x (int): 单元格列
            y (int): 单元格行
            is_context (bool): 是否为上下文（鼠标右键）单击？
        """
        self.x, self.y, self.is_context = x, y, is_context
