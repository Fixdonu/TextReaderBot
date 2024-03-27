# screen_select.py
import tkinter as tk

class ScreenSelect(tk.Toplevel):
    def __init__(self, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.begin_x = None
        self.begin_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None  # Ensure rect is initialized here

        self.canvas = tk.Canvas(self, cursor="cross", bg='grey', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.attributes("-fullscreen", True, "-alpha", 0.3)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.begin_x = event.x
        self.begin_y = event.y

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.begin_x, self.begin_y, curX, curY, outline='red', width=2)
        else:
            self.canvas.coords(self.rect, self.begin_x, self.begin_y, curX, curY)

    def on_button_release(self, event):
        self.end_x, self.end_y = (event.x, event.y)
        self.destroy()
        self.callback(self.begin_x, self.begin_y, self.end_x, self.end_y)
