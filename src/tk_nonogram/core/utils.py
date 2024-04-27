from collections import deque
from typing import Sequence

from numpy import array, ndarray, zeros
from numpy.dtypes import Int8DType
from numpy.random import randint

from ..utils import Activity

MatrixLike = Sequence[Sequence[int]]
Puzzle = ndarray[tuple[int, int], Int8DType]
Row = ndarray[tuple[int], Int8DType]
LogStack = deque[Activity]


class GameCore:
    """
    游戏内核

    Properties:
        answer (Puzzle): 题解
        clues (Clues): 线索
        grid (Puzzle): 当前游戏面板
        undo_log (LogStack): 撤回操作栈
        redo_log (LogStack): 重做操作栈
    """

    class Clues:
        """线索"""

        def __init__(
            self, rows: Sequence[tuple[int]] | None = None, columns: Sequence[tuple[int]] | None = None
        ) -> None:
            self.rows: Sequence[tuple[int]] = rows or []
            self.columns: Sequence[tuple[int]] = columns or []

        def __eq__(self, value: object) -> bool:
            return (
                (self.rows == value.rows and self.columns == value.columns)
                if isinstance(value, GameCore.Clues)
                else False
            )

        def __repr__(self) -> str:
            return f"Clues(rows={self.rows}, columns={self.columns})"

    def __init__(self, level: int = 10) -> None:
        self.grid: Puzzle = zeros((level, level), dtype=Int8DType)
        self.undo_log: deque[Activity] = deque()
        self.redo_log: deque[Activity] = deque()

    def count_continues(self, _row: Row) -> tuple[int]:
        """
        统计 NumPy 矩阵单行/列中连续 1 的数量

        Args:
            _array (Row): NumPy 二维矩阵

        Returns:
            tuple[int]: 数量列表，用作解题线索
        """
        from numpy import append, diff, insert, where

        # 参考文献： [计算连续出现次数](https://geek-docs.com/numpy/numpy-ask-answer/231_numpy_count_consecutive_occurences_of_values_varying_in_length_in_a_numpy_array.html#ftoc-heading-2)  ## noqa: B950
        # 找到数组中所有的1
        ones = where(_row == 1)[0]
        # 计算连续1的起始索引和结束索引
        diff = diff(ones)  # type: ignore[assignment]
        starts = insert(where(diff != 1)[0] + 1, 0, 0)
        ends = append(where(diff != 1)[0], len(ones) - 1)
        # 计算连续1的长度
        lengths = ends - starts + 1

        return tuple(lengths.tolist())

    def generate_clues(self, _matrix: Puzzle | MatrixLike | None = None) -> Clues:
        """
        生成线索（谜面）

        Args:
            _matrix (Puzzle | MatrixLike): 游戏板状态二维矩阵

        Returns:
            Clues: 线索字典
        """
        from numpy import array

        if _matrix is None:
            _matrix = self.answer
        elif not isinstance(_matrix, ndarray):
            # 当传入参数不是 NumPy 矩阵时，转换为矩阵
            _matrix = array(_matrix)
        # 提取矩阵规模
        rows, cols = _matrix.shape
        if rows <= 0 or cols <= 0:
            # 当矩阵某一个维度为 0 ，不可能存在谜面
            return self.Clues()
        row_clues = [self.count_continues(_matrix[_, :]) for _ in range(rows)]
        col_clues = [self.count_continues(_matrix[:, _]) for _ in range(cols)]
        self.clues = self.Clues(row_clues, col_clues)
        return self.clues

    def generate_puzzle(self, level: int = 10) -> None:
        """
        随机生成数织题解

        【注意】此种随机生成无法保证题目存在唯一逻辑解，甚至可能不存在逻辑解（逻辑求解算法无解）

        Returns:
            Puzzle: 随机 0-1 二维 NumPy 矩阵
        """
        self.answer = randint(0, 2, (level, level))

    def load_file(self, filename: str | None) -> bool:
        """
        加载题解，根据题解还原谜题

        Returns:
            (bool): 文件是否解析成功？
        """
        if filename:
            with open(filename, encoding="UTF-8") as file:
                data = file.readlines()
            try:
                self.answer = array([[int(col) for col in row.strip()] for row in data], dtype=Int8DType)
                return True
            except Exception:
                pass
        return False

    def toggle_cell(self, activity: Activity) -> None:
        """
        切换单元格状态

        Args:
            activity (Activity): 用户操作
        """
        if activity.is_context:
            self.grid[activity.y, activity.x] = 0 if self.grid[activity.y, activity.x] == 2 else 2
        else:
            self.grid[activity.y, activity.x] = 0 if self.grid[activity.y, activity.x] == 1 else 1

    def undo(self) -> Activity | None:
        """
        撤销至上一步

        Returns:
            (Activity | None): 能够撤销时，返回本次撤销的操作；无法撤销时返回 `None`
        """
        if self.undo_log:
            # pop() 操作会在空双向队列是触发 IndexError
            activity = self.undo_log.pop()
            self.toggle_cell(activity)
            self.redo_log.append(activity)
            return activity
        return None

    def redo(self) -> Activity | None:
        """
        重做下一步

        Returns:
            (Activity | None): 能够重做时，返回本次重做的操作；无法重做时返回 `None`
        """
        if self.redo_log:
            activity = self.redo_log.pop()
            self.toggle_cell(activity)
            self.undo_log.append(activity)
            return activity
        return None

    def move(self, activity: Activity) -> None:
        """
        执行一次游戏移动

        「移动」特指用户的一次交互，不管是用户左击还是右击

        Args:
            activity (Activity): 用户操作
        """
        self.toggle_cell(activity)
        self.undo_log.append(activity)
        self.redo_log.clear()

    def is_solved(self) -> bool:
        """检查谜题是否已被用户求解成功"""
        current = self.generate_clues(self.grid)
        return current == self.clues

    def get_answer(self) -> str:
        """获取字符串形式的题解"""
        return "\n".join("".join(map(lambda _: "[X]" if _ else "[ ]", r)) for r in self.answer)
