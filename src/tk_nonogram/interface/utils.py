from functools import partial
from tkinter import Button, Canvas, Event, Label, Misc, Tk, Toplevel
from tkinter.filedialog import askopenfilename
from tkinter.font import Font
from tkinter.messagebox import askyesno, showerror, showinfo, showwarning
from tkinter.simpledialog import askinteger
from typing import Any

from _tkinter import Tcl_Obj

from ..core.utils import GameCore
from ..utils import Activity


class GameUI:
    """数织"""

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

    def __init__(self) -> None:
        """初始化游戏"""
        self.core = GameCore()
        self.__init_window()

    def __init_window(self) -> None:
        """初始化图形显示界面"""
        if self.ask_puzzle_type():
            if not self.core.load_file(self.ask_file()):
                self.ask_level()
                self.core.generate_puzzle(self.level)
        else:
            self.ask_level()
            self.core.generate_puzzle(self.level)
        self.core.generate_clues()
        self.ask_cell_size()
        self.offset = self.level * self.cell_size // 2
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

    def ask_cell_size(self) -> None:
        """
        询问谜题单元格大小

        当用户不指定大小时，默认为 25px
        """
        self.cell_size = askinteger("Input", "请输入单个方块的边长（px）：") or 25

    def ask_file(self) -> str:
        """
        选择一个文件

        Returns:
            str: 文件路径
        """
        return askopenfilename(filetypes=[("Text files", "*.txt")])

    def ask_level(self) -> None:
        """询问难度等级"""
        _ = askinteger("Input", "请输入难度级别：")
        if _ and _ >= 0:
            self.level = _
        else:
            self.level = 10

    def ask_puzzle_type(self) -> bool:
        """
        选择数织谜题来源，根据来源获取题解矩阵

        Returns:
            bool: `True` 从文件加载， `False` 随机生成题目
        """
        return askyesno("题目模式", "是否从题解文件加载生成题目？")

    def bind_events(self) -> None:
        """绑定鼠标事件"""
        self.canvas.bind_all("<Button-1>", partial(self.on_click, is_context=False))
        self.canvas.bind_all("<Button-3>", partial(self.on_click, is_context=True))
        self.canvas.bind_all("<Control-z>", self.undo)
        self.canvas.bind_all("<Control-r>", self.redo)

    def check_solution(self) -> None:
        if self.core.is_solved():
            showinfo("Contratulations", "您成功解决了此数织！")
        else:
            showwarning("Oops", "您的题解有误！")
        action = askyesno("Choice", "是否需要为您展示正确题解？")
        if action:
            self.SolutionDialog(title="Answer", message=self.core.get_answer(), font=self.MONOSPACE)

    def draw_grid_with_clues(self) -> None:
        """绘制带有题目线索的数织网格"""
        self.canvas.delete("all")
        # Draw clues for rows
        text_y = self.offset + self.cell_size // 2  # Starting position for row clues
        for _, clue in enumerate(self.core.clues.rows):
            text = " ".join(map(str, clue))
            self.canvas.create_text(  # type: ignore
                self.offset - self.cell_size,
                text_y,
                text=text,
                fill="black",
                tag="clue",
                font=self.MONOSPACE,
                anchor=self.Direction.EAST,
            )
            text_y += self.cell_size  # Move to the next line for the next clue
        # Draw clues for columns
        text_x = self.offset + self.cell_size // 2  # Starting position for column clues
        for _, clue in enumerate(self.core.clues.columns):
            text = "\n".join(map(str, clue))
            self.canvas.create_text(  # type: ignore
                text_x,
                self.offset - self.cell_size,
                text=text,
                fill="black",
                tag="clue",
                # angle=-90,
                font=self.MONOSPACE,
                anchor=self.Direction.SOUTH,
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
            self.core.move(Activity(x, y, is_context))
            self.update_cell_visuals(x, y, is_context)

    def redo(self, _: Event) -> None:
        """
        重做下一步

        Args:
            _ (Event): TKinter 事件
        """
        activity = self.core.redo()
        if activity:
            self.update_cell_visuals(activity.x, activity.y, activity.is_context)

    def undo(self, _: Event) -> None:
        """
        撤销至上一步

        Args:
            _ (Event): TKinter 事件
        """
        activity = self.core.undo()
        if activity:
            self.update_cell_visuals(activity.x, activity.y, activity.is_context)

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
            if status := self.core.grid[row, col]:
                self.canvas.itemconfig(cell, fill=("grey" if (status - 1) else "blue"))  # type: ignore
            else:
                self.canvas.itemconfig(cell, fill="white")  # type: ignore
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=("grey" if is_context else "blue"), tag=tag)  # type: ignore
