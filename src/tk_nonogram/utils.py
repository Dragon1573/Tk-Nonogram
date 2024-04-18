from typing import Sequence

from numpy import ndarray
from numpy.dtypes import Int8DType

MatrixLike = Sequence[Sequence[int]]
Puzzle = ndarray[tuple[int, int], Int8DType]
Row = ndarray[tuple[int], Int8DType]


class Clues:
    """线索"""

    def __init__(self, rows: Sequence[tuple[int]] | None = None, columns: Sequence[tuple[int]] | None = None) -> None:
        self.rows: Sequence[tuple[int]] = rows or []
        self.columns: Sequence[tuple[int]] = columns or []

    def __eq__(self, value: object) -> bool:
        return (self.rows == value.rows and self.columns == value.columns) if isinstance(value, Clues) else False


def count_continues(_row: Row) -> tuple[int]:
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

    return lengths.tolist()


def generate_clues(_matrix: Puzzle | MatrixLike) -> Clues:
    """
    生成线索（谜面）

    Args:
        _matrix (Puzzle | MatrixLike): 游戏板状态二维矩阵

    Returns:
        dict[str, list[int]]: 线索字典
    """
    from numpy import array

    if not isinstance(_matrix, ndarray):
        # 当传入参数不是 NumPy 矩阵时，转换为矩阵
        _matrix = array(_matrix)
    # 提取矩阵规模
    rows, cols = _matrix.shape
    if rows <= 0 or cols <= 0:
        # 当矩阵某一个维度为 0 ，不可能存在谜面
        return Clues()
    row_clues = [count_continues(_matrix[_, :]) for _ in range(rows)]
    col_clues = [count_continues(_matrix[:, _]) for _ in range(cols)]
    return Clues(row_clues, col_clues)
