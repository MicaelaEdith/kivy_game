from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase
from kivy.uix.image import Image
from kivy.uix.button import Button
import random

LabelBase.register(name="Lobster", fn_regular="assets/Lobster-Regular.ttf")


Window.fullscreen = 'auto'

Builder.load_file("board.kv")

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


class TileWidget(FloatLayout):
    def __init__(self, value, direction=None, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.size_hint = (1, 1)

        color = get_tile_color(value)
        r, g, b = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]

        with self.canvas.before:
            Color(r, g, b, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

        self.bind(pos=lambda inst, val: setattr(self.bg_rect, 'pos', val))
        self.bind(size=lambda inst, val: setattr(self.bg_rect, 'size', val))

        if value:
            self.label = Label(
                text=str(value),
                font_size=65,
                bold=True,
                color=(0.4, 0.2, 0.1, 1),
                size_hint=(1, 1),
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            )
            self.add_widget(self.label)
            if direction:
                self.animate(direction)

    def animate(self, direction):
        dx, dy = {
            'left': (-3, 0),
            'right': (3, 0),
            'up': (0, 3),
            'down': (0, -3)
        }.get(direction, (0, 0))

        anim = Animation(pos_hint={"center_x": 0.5 + dx/100.0, "center_y": 0.5 + dy/100.0}, duration=0.1) + \
               Animation(pos_hint={"center_x": 0.5, "center_y": 0.5}, duration=0.1)
        anim.start(self.label)


class Board(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.won = False
        Clock.schedule_once(self.init_board, 0)

    def init_board(self, *args):
        self.add_random_tile()
        self.add_random_tile()
        self.update_board()

    def exit_game(self, *args):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(StartScreen(app.start_game))
        app.in_game = False

    def add_random_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = random.choice([2, 4])

    def update_board(self, direction=None):
        grid = self.ids.grid
        grid.clear_widgets()
        found_2048 = False
        for row in self.board:
            for value in row:
                if value == 2048:
                    found_2048 = True
                tile = TileWidget(value, direction=direction)
                grid.add_widget(tile)
        self.update_score(self.score)

        if found_2048 and not self.won:
            self.won = True
            self.show_win_label()

    def show_win_label(self):
        label = self.ids.win_label
        anim = Animation(opacity=1, duration=3) + Animation(opacity=0, duration=1)
        anim.start(label)

    def move_left(self):
        for r in range(4):
            self.board[r], added = self.merge(self.board[r])
            self.score += added
        self.add_random_tile()
        self.update_board(direction='left')

    def move_right(self):
        for r in range(4):
            reversed_row = list(reversed(self.board[r]))
            merged, added = self.merge(reversed_row)
            self.board[r] = list(reversed(merged))
            self.score += added
        self.add_random_tile()
        self.update_board(direction='right')

    def move_up(self):
        self.board = list(map(list, zip(*self.board)))
        for r in range(4):
            self.board[r], added = self.merge(self.board[r])
            self.score += added
        self.board = list(map(list, zip(*self.board)))
        self.add_random_tile()
        self.update_board(direction='up')

    def move_down(self):
        self.board = list(map(list, zip(*self.board)))
        for r in range(4):
            reversed_row = list(reversed(self.board[r]))
            merged, added = self.merge(reversed_row)
            self.board[r] = list(reversed(merged))
            self.score += added
        self.board = list(map(list, zip(*self.board)))
        self.add_random_tile()
        self.update_board(direction='down')

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


class StartScreen(FloatLayout):
    def __init__(self, start_callback, **kwargs):
        super().__init__(**kwargs)
        self.start_callback = start_callback
        with self.canvas.before:
            Color(1, 0.55, 0.82, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda instance, value: setattr(self.bg, 'pos', value))
        self.bind(size=lambda instance, value: setattr(self.bg, 'size', value))

        self.label = Label(
            text="Tap to Start",
            font_size=80,
            font_name="Lobster",
            color=(1.0, 0.92, 0.70, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.add_widget(self.label)

    def on_touch_down(self, touch):
        self.start_callback()
        return True


class Game2048App(App):
    def build(self):
        self.root_widget = FloatLayout()
        self.in_game = False
        self.start_screen = StartScreen(start_callback=self.start_game)
        self.root_widget.add_widget(self.start_screen)
        return self.root_widget

    def start_game(self):
        if not self.in_game:
            self.in_game = True
            self.root_widget.clear_widgets()
            self.board = Board()
            self.root_widget.add_widget(self.board)


if __name__ == "__main__":
    Game2048App().run()
