from _tkinter import Tcl_Obj
from collections import deque
from functools import partial
from tkinter import Button, Canvas, Event, Label, Misc, Tk, Toplevel
from tkinter.font import Font
from tkinter.messagebox import askyesno, showerror, showinfo, showwarning
from typing import Any

from numpy import ndarray, zeros
from numpy.dtypes import IntDType

from .utils import Clues, Puzzle, generate_clues


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


class Direction:
    """Tkinter 文本对齐方向"""

    EAST = "e"
    SOUTH = "s"


class SolutionDialog(Toplevel):
    """
    题解对话框

    `tkinter.messagebox` 中提供的预置对话框都不支持指定字体格式，
    我们需要自己继承 `tkinter.Toplevel` 类以实现一个自定义的对话框
    """

    def __init__(
        self,
        master: Misc | None = None,
        *,
        title: str | None = None,
        message: float | str = "",
        font: str | Font | list[Any] | tuple[Any, ...] | Tcl_Obj = "TkDefaultFont",
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.message = message
        self.font = font
        self.label = Label(self, text=self.message, font=self.font)
        self.label.pack(padx=10, pady=10)
        self.button = Button(self, text="OK", command=self.ok)
        self.button.pack(pady=10)

    def ok(self) -> None:
        self.destroy()


class Nonogram:
    """数织"""

    def __init_window(self) -> None:
        """初始化图形显示界面"""
        self.window = Tk()
        self.MONOSPACE = Font(family="Consolas", size=self.cell_size // 2)
        MAXIMUM_PIXEL = min(self.window.winfo_screenheight(), self.window.winfo_screenwidth())
        self.pixel = self.level * self.cell_size + self.offset
        if MAXIMUM_PIXEL < self.pixel:
            showerror("Error", "窗口尺寸超出屏幕范围！")
            showerror("Error", "应用因意外情况退出！")
            exit(-1)
        self.window.geometry(f"{self.pixel}x{self.pixel}+0+0")
        self.window.resizable(False, False)
        self.window.title("数织")
        self.button_size = self.offset
        self.canvas = Canvas(self.window, width=self.pixel, height=self.pixel)
        self.canvas.pack()
        self.draw_grid_with_clues()
        self.bind_events()
        self.button = Button(
            self.window,
            text="提交",
            command=self.check_solution,
            width=self.button_size,
            height=self.button_size,
            font=self.MONOSPACE,
        )
        self.button.place(x=0, y=0, width=self.button_size, height=self.button_size)
        self.window.mainloop()

    def __init__(self, clues: Clues, answer: Puzzle, cell_size: int = 25) -> None:
        """
        初始化游戏

        Args:
            clues (Clues): 题面线索
            answer (Puzzle): 二维题解矩阵
            cell_size (int, optional): 单元格边长，默认长度为 25px
        """
        assert isinstance(answer, ndarray), "未设置题解！"
        self.__answer = "\n".join("".join(map(lambda _: "[X]" if _ else "[ ]", r)) for r in answer)
        self.level, self.cell_size, self.clues = answer.shape[0], cell_size, clues
        self.offset = self.level * self.cell_size // 2
        self.grid: Puzzle = zeros((self.level, self.level), dtype=IntDType)
        self.undo_log: deque[Activity] = deque()
        self.redo_log: deque[Activity] = deque()
        self.__init_window()

    def toggle_cell(self, x: int, y: int, is_context: bool) -> None:
        """
        切换单元格状态

        Args:
            x (int): 单元格列
            y (int): 单元格行
            is_context (bool): 是否为上下文（鼠标右键）单击？
        """
        if is_context:
            self.grid[y, x] = 0 if self.grid[y, x] == 2 else 2
        else:
            self.grid[y, x] = 0 if self.grid[y, x] == 1 else 1

    def update_cell_visuals(self, col: int, row: int, is_context: bool) -> None:
        """
        更新单元格视觉效果

        Args:
            col (int): 单元格列
            row (int): 单元格行
            is_context (bool): 是否为上下文（鼠标右键）单击？
        """
        x1 = self.offset + col * self.cell_size
        y1 = self.offset + row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        tag = f"cell_{row}_{col}"
        cell = self.canvas.find_withtag(tag)
        if cell:
            if status := self.grid[row, col]:
                self.canvas.itemconfig(cell, fill=("grey" if (status - 1) else "blue"))  # type: ignore
            else:
                self.canvas.itemconfig(cell, fill="white")  # type: ignore
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=("grey" if is_context else "blue"), tag=tag)  # type: ignore

    def undo(self, _: Event) -> None:
        """
        撤销至上一步

        Args:
            _ (Event): TKinter 事件
        """
        if self.undo_log:
            # pop() 操作会在空双向队列是触发 IndexError
            activity = self.undo_log.pop()
            self.toggle_cell(activity.x, activity.y, activity.is_context)
            self.update_cell_visuals(activity.x, activity.y, activity.is_context)
            self.redo_log.append(activity)

    def redo(self, _: Event) -> None:
        """
        重做下一步

        Args:
            _ (Event): TKinter 事件
        """
        if self.redo_log:
            activity = self.redo_log.pop()
            self.toggle_cell(activity.x, activity.y, activity.is_context)
            self.update_cell_visuals(activity.x, activity.y, activity.is_context)
            self.undo_log.append(activity)

    def on_click(self, event: Event, is_context: bool) -> None:
        """
        鼠标事件处理器

        Args:
            event (Event): Tkinter 事件实例
            is_context (bool): 是否为上下文（鼠标右键）单击？
        """
        x = (event.x - self.offset) // self.cell_size
        y = (event.y - self.offset) // self.cell_size
        if 0 <= x < self.level and 0 <= y < self.level:
            self.toggle_cell(x, y, is_context)
            self.update_cell_visuals(x, y, is_context)
            self.undo_log.append(Activity(x, y, is_context))
            self.redo_log.clear()

    def bind_events(self) -> None:
        """绑定鼠标事件"""
        self.canvas.bind_all("<Button-1>", partial(self.on_click, is_context=False))
        self.canvas.bind_all("<Button-3>", partial(self.on_click, is_context=True))
        self.canvas.bind_all("<Control-z>", self.undo)
        self.canvas.bind_all("<Control-r>", self.redo)

    def draw_grid_with_clues(self) -> None:
        """绘制带有题目线索的数织网格"""
        self.canvas.delete("all")
        # Draw clues for rows
        text_y = self.offset + self.cell_size // 2  # Starting position for row clues
        for _, clue in enumerate(self.clues.rows):
            text = " ".join(map(str, clue))
            self.canvas.create_text(  # type: ignore
                self.offset - self.cell_size,
                text_y,
                text=text,
                fill="black",
                tag="clue",
                font=self.MONOSPACE,
                anchor=Direction.EAST,
            )
            text_y += self.cell_size  # Move to the next line for the next clue
        # Draw clues for columns
        text_x = self.offset + self.cell_size // 2  # Starting position for column clues
        for _, clue in enumerate(self.clues.columns):
            text = "\n".join(map(str, clue))
            self.canvas.create_text(  # type: ignore
                text_x,
                self.offset - self.cell_size,
                text=text,
                fill="black",
                tag="clue",
                # angle=-90,
                font=self.MONOSPACE,
                anchor=Direction.SOUTH,
            )
            text_x += self.cell_size  # Move to the right for the next clue
        # Draw the grid cells
        cell_x = self.offset  # Starting position for grid cells (after clues)
        cell_y = self.offset
        for _ in range(self.level):
            for _ in range(self.level):
                self.canvas.create_rectangle(  # type: ignore
                    cell_x,
                    cell_y,
                    cell_x + self.cell_size,
                    cell_y + self.cell_size,
                    fill="white",
                    tag="cell",
                )
                cell_x += self.cell_size
            cell_x = self.offset  # Reset x position for the next row
            cell_y += self.cell_size

    def check_solution(self) -> None:
        current = generate_clues(self.grid)
        if current == self.clues:
            showinfo("Contratulations", "您成功解决了此数织！")
        else:
            showwarning("Oops", "您的题解有误！")
        action = askyesno("Choice", "是否需要为您展示正确题解？")
        if action:
            SolutionDialog(title="Answer", message=self.__answer, font=self.MONOSPACE)
