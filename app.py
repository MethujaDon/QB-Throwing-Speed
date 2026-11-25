"""
app.py  -  my demo app.   Run it with:  python app.py

Three panels:
  left   - pick a throw from the list
  middle - the throw drawn in 3D on the field
  right  - the calculation, step by step
The bar along the top turns red if the throw is impossible.
"""

import math
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from field3d import COLORS, draw_field
from throw_speed import (CATCH_HEIGHT, EYE_HEIGHT, G, MAX_SPEED_MPH, analyze, ball_path, load_throws)


def find_data_file():
    """Use data/throws.xlsx next to the app if it is there, otherwise the copy packed inside the app."""
    if getattr(sys, "frozen", False):                       # running as the .exe
        here = os.path.dirname(sys.executable)
        packed = os.path.join(sys._MEIPASS, "data", "throws.xlsx")
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        packed = os.path.join(here, "data", "throws.xlsx")
    beside = os.path.join(here, "data", "throws.xlsx")
    return beside if os.path.exists(beside) else packed


def calculation_text(row):
    """The working for one throw, the same steps as in my report."""
    dz = CATCH_HEIGHT - EYE_HEIGHT
    d_ft = row["distance_yd"] * 3
    a = row["angle"]
    lines = [
        f"THROW #{row['number']}",
        f"{row['Game']}",
        f"Goff to {row['Catcher']}  ({row['result']})",
        "",
        "1. Distance on the ground",
        f"   sideways gap = {row['catch_x']:.1f} - ({row['throw_x']:.1f}) = {row['catch_x'] - row['throw_x']:.1f} yd",
        f"   along gap    = {row['catch_y']:.1f} - {row['throw_y']:.1f} = {row['catch_y'] - row['throw_y']:.1f} yd",
        f"   d = sqrt(sideways^2 + along^2)",
        f"     = {row['distance_yd']:.1f} yd = {d_ft:.1f} ft",
        "",
        "2. Height change",
        f"   dz = catch - release",
        f"      = {CATCH_HEIGHT} - {EYE_HEIGHT} = {dz} ft",
        "",
        "3. Angle above Goff's eye line",
        f"   angle = {a:g} degrees",
        "",
        "4. Launch speed",
        "   V = sqrt( g d^2 /",
        "       (2 cos^2(angle) (d tan(angle) - dz)) )",
    ]
    if row["check"] == "impossible angle":
        top = d_ft * math.tan(math.radians(a)) - dz
        lines += [
            f"   d tan(angle) - dz = {top:.1f}",
            "   This is 0 or less, so the bottom of the",
            "   fraction is not positive. No speed works.",
            "   -> IMPOSSIBLE",
        ]
        return "\n".join(lines)
    rad = math.radians(a)
    bottom = 2 * math.cos(rad) ** 2 * (d_ft * math.tan(rad) - dz)
    v_fps = row["speed_mph"] * 5280 / 3600
    lines += [
        f"   = sqrt( {G} x {d_ft:.1f}^2 / {bottom:.1f} )",
        f"   = {v_fps:.1f} ft/s",
        f"   = {row['speed_mph']:.1f} mph",
        "",
        "5. Time in the air",
        f"   t = d / (V cos(angle)) = {row['hang_time_s']} s",
    ]
    if row["check"] == "too fast to be real":
        lines += ["", f"   Over {MAX_SPEED_MPH} mph, so this is not a",
                  "   realistic NFL throw. The angle is",
                  "   probably too flat. -> IMPOSSIBLE"]
    return "\n".join(lines)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("How Fast Does He Really Throw?")
        self.geometry("1250x720")

        # Top: the possible / impossible bar
        self.banner = tk.Label(self, text="", font=("Arial", 16, "bold"), fg="white", bg="gray", pady=8)
        self.banner.pack(fill=tk.X)

        main = tk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True)

        # Left panel: pick a throw
        left = tk.Frame(main, padx=8, pady=8)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Pick a throw", font=("Arial", 12, "bold")).pack(anchor="w")
        self.listbox = tk.Listbox(left, width=34, font=("Courier", 10), activestyle="none")
        self.listbox.pack(fill=tk.Y, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.show_throw)
        tk.Button(left, text="Open a different data file", command=self.open_file).pack(fill=tk.X, pady=(6, 0))

        # Right panel: the calculation
        right = tk.Frame(main, padx=8, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(right, text="The calculation", font=("Arial", 12, "bold")).pack(anchor="w")
        self.calc = tk.Text(right, width=46, font=("Courier", 10), bg="#F4F6F8")
        self.calc.pack(fill=tk.Y, expand=True)

        # Middle panel: the throw in 3D
        middle = tk.Frame(main, pady=8)
        middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(middle, text="The throw in 3D (drag to turn it)", font=("Arial", 12, "bold")).pack(anchor="w")
        self.figure = Figure(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=middle)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.load(find_data_file())

    def load(self, path):
        try:
            self.df = analyze(load_throws(path))
        except Exception as error:
            messagebox.showerror("Could not read the file", str(error))
            return
        self.listbox.delete(0, tk.END)
        for _, row in self.df.iterrows():
            mark = "OK " if row["check"] == "OK" else "X  "
            self.listbox.insert(tk.END, f"{mark}#{row['number']:<3}{row['Catcher']:<13}{row['angle']:>4g} deg")
            if row["check"] != "OK":
                self.listbox.itemconfig(tk.END, fg="red")
        self.listbox.selection_set(0)
        self.show_throw()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if path:
            self.load(path)

    def show_throw(self, event=None):
        picked = self.listbox.curselection()
        if not picked:
            return
        row = self.df.iloc[picked[0]]

        # The possible / impossible bar
        if row["check"] == "OK":
            self.banner.config(text=f"Throw #{row['number']} is possible:  {row['speed_mph']:.1f} mph", bg="#2E7D32")
        else:
            self.banner.config(text=f"Throw #{row['number']} is IMPOSSIBLE:  {row['check']}", bg="#C8102E")

        # The calculation
        self.calc.delete("1.0", tk.END)
        self.calc.insert(tk.END, calculation_text(row))

        # The 3D picture
        self.figure.clear()
        ax = self.figure.add_subplot(projection="3d")
        first = min(row["throw_y"], row["catch_y"]) - 5
        last = max(row["throw_y"], row["catch_y"]) + 5
        draw_field(ax, first, last)
        if row["check"] == "OK":
            along, sideways, height = ball_path(row)
            ax.plot(along, sideways, height, color=COLORS[row["result"]], linewidth=3, zorder=3)
            ax.set_zlim(0, max(height) + 5)
            ax.set_title(f"{row['distance_yd']} yd, {row['angle']:g} degrees, {row['speed_mph']:.1f} mph")
        else:
            # No real arc, so just show the throw and catch spots joined by a dashed red line
            ax.plot([row["throw_y"], row["catch_y"]], [row["throw_x"], row["catch_x"]], [EYE_HEIGHT, CATCH_HEIGHT],
                    "r--", linewidth=2, zorder=3)
            ax.set_zlim(0, 20)
            ax.set_title("No real arc for this throw", color="#C8102E")
        ax.scatter(row["throw_y"], row["throw_x"], EYE_HEIGHT, color="black", s=40, zorder=4)
        ax.text(row["throw_y"], row["throw_x"], EYE_HEIGHT + 2, "throw", zorder=5)
        ax.scatter(row["catch_y"], row["catch_x"], CATCH_HEIGHT, color="red", s=40, zorder=4)
        ax.text(row["catch_y"], row["catch_x"], CATCH_HEIGHT + 2, "catch", zorder=5)
        ax.set_xlim(first, last)
        ax.set_ylim(-27, 27)
        ax.view_init(elev=20, azim=-70)
        ax.tick_params(labelsize=8)                       # smaller numbers so everything fits
        for label in (ax.xaxis.label, ax.yaxis.label, ax.zaxis.label):
            label.set_size(9)
        ax.title.set_size(12)
        self.figure.subplots_adjust(left=0, right=0.93, bottom=0.03, top=0.93)
        self.canvas.draw()


if __name__ == "__main__":
    App().mainloop()
