from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window

Window.fullscreen = 'auto'

import random

KV = Builder.load_file("board.kv")

COLORS = {
    2: "#FFF5CC",
    4: "#FFEBB3",
    8: "#FFE099",
    16: "#FFD480",
    32: "#FFC966",
    64: "#FFBF80",
    128: "#FFB3A2",
    256: "#FFA6B3",
    512: "#FF99C2",
    1024: "#FF8CD1",
    2048: "#FF80E0",
}

def get_tile_color(num):
    return COLORS.get(num, "#FFF5CC")

class Board(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = [[0] * 4 for _ in range(4)]
        self.score = 0
        Clock.schedule_once(self.init_board, 0)

    def init_board(self, *args):
        self.add_random_tile()
        self.add_random_tile()
        self.update_board()

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = random.choice([2, 4])

    def update_board(self):
        grid = self.ids.grid
        grid.clear_widgets()
        for row in self.board:
            for value in row:
                color = get_tile_color(value)
                btn = Button(
                    text=str(value) if value else "",
                    font_size=45,
                    bold=True,
                    background_normal='',
                    background_color=(1, 1, 1, 0),
                    color=(0.4, 0.2, 0.1, 1) if value else (0.6, 0.6, 0.6, 1),
                )
                with btn.canvas.before:
                    r, g, b = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
                    Color(r, g, b, 1)
                    btn.bg_rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[12])
                btn.bind(pos=lambda inst, val: setattr(inst.bg_rect, 'pos', val))
                btn.bind(size=lambda inst, val: setattr(inst.bg_rect, 'size', val))
                grid.add_widget(btn)
        self.update_score(self.score)

    def move_left(self):
        for r in range(4):
            self.board[r], added = self.merge(self.board[r])
            self.score += added
        self.add_random_tile()
        self.update_board()

    def move_right(self):
        for r in range(4):
            reversed_row = list(reversed(self.board[r]))
            merged, added = self.merge(reversed_row)
            self.board[r] = list(reversed(merged))
            self.score += added
        self.add_random_tile()
        self.update_board()

    def move_up(self):
        self.board = list(map(list, zip(*self.board)))
        for r in range(4):
            self.board[r], added = self.merge(self.board[r])
            self.score += added
        self.board = list(map(list, zip(*self.board)))
        self.add_random_tile()
        self.update_board()

    def move_down(self):
        self.board = list(map(list, zip(*self.board)))
        for r in range(4):
            reversed_row = list(reversed(self.board[r]))
            merged, added = self.merge(reversed_row)
            self.board[r] = list(reversed(merged))
            self.score += added
        self.board = list(map(list, zip(*self.board)))
        self.add_random_tile()
        self.update_board()

    def merge(self, row):
        new_row = [num for num in row if num != 0]
        merged_row = []
        skip = False
        score_add = 0
        for i in range(len(new_row)):
            if skip:
                skip = False
                continue
            if i < len(new_row) - 1 and new_row[i] == new_row[i + 1]:
                merged_value = new_row[i] * 2
                merged_row.append(merged_value)
                score_add += merged_value
                skip = True
            else:
                merged_row.append(new_row[i])
        merged_row += [0] * (4 - len(merged_row))
        return merged_row, score_add

    def on_touch_up(self, touch):
        if abs(touch.x - touch.opos[0]) > abs(touch.y - touch.opos[1]):
            if touch.x > touch.opos[0]:
                self.move_right()
            else:
                self.move_left()
        else:
            if touch.y > touch.opos[1]:
                self.move_up()
            else:
                self.move_down()

    def update_score(self, points):
        self.ids.score_label.text = f"Score : {points}"

class Game2048App(App):
    def build(self):
        return Board()

if __name__ == "__main__":
    Game2048App().run()