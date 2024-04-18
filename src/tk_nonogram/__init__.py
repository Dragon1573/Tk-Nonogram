from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askyesno, showerror, showinfo
from tkinter.simpledialog import askinteger

from numpy import array
from numpy.dtypes import Int8DType
from numpy.random import randint

from .entities import Nonogram  # type: ignore[import-untyped]
from .utils import Puzzle, generate_clues  # type: ignore[import-untyped]

__version__ = "0.2.1"
__all__ = ["main"]


def generate_puzzle() -> Puzzle:
    """
    随机生成数织题解

    【注意】此种随机生成无法保证题目存在唯一逻辑解，甚至可能不存在逻辑解（逻辑求解算法无解）

    Returns:
        Puzzle: 随机 0-1 二维 NumPy 矩阵
    """
    if (level := askinteger("Input", "请输入难度级别：")) and level > 0:
        return randint(0, 2, (level, level))
    showinfo("Tips", "已默认设置为 10×10 难度！")
    return randint(0, 2, (10, 10))


def load_file() -> Puzzle:
    """
    加载题解，根据题解还原谜题

    Returns:
        Puzzle: 题解二维 NumPy 矩阵
    """
    if filename := askopenfilename(filetypes=[("Text files", "*.txt")]):
        with open(filename, encoding="UTF-8") as file:
            data = file.readlines()
        return array([[int(col) for col in row.strip()] for row in data], dtype=Int8DType)
    return generate_puzzle()


def pick_puzzle_type() -> Puzzle:
    """
    选择数织谜题来源，根据来源获取题解矩阵

    Returns:
        Puzzle: 二维 NumPy 矩阵
    """
    return load_file() if askyesno("题目模式", "是否从题解文件加载生成题目？") else generate_puzzle()


def ask_cell_size() -> int:
    size = askinteger("Input", "请输入单个方块的边长（px）：")
    return size if (size and size > 0) else 25


def main() -> None:
    """应用程序入口"""
    answer = pick_puzzle_type()
    if answer.shape[0] != answer.shape[1]:
        showerror("Error", "题解数据不合理或不是方阵！")
        showerror("Exit", "因意外情况而退出！")
        exit(-1)
    clues = generate_clues(answer)
    cell_size = ask_cell_size()
    Nonogram(clues, answer, cell_size)
