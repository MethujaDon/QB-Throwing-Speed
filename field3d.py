"""
field3d.py

The 3D part of my project: a football field with every throw drawn as an arc,
plus a close-up of one throw and an animated GIF of the ball flying.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from throw_speed import ball_path

LIONS_BLUE = "#0076B6"
GOLD = "#F2A900"
COLORS = {"Complete": LIONS_BLUE, "Touchdown": GOLD}


def draw_field(ax, first_yard=-10, last_yard=110):
    """Green field, blue end zones, and white lines every 10 yards. 0 = the Lions' goal line.
    first_yard and last_yard let me draw only part of the field for a close-up
    (matplotlib 3D does not cut off things outside the axes, so I only draw what fits)."""
    ax.computed_zorder = False                     # draw things in the order I add them
    sides = [-26.65, 26.65]                        # the field is 53.3 yards wide
    pieces = [(-10, 0, LIONS_BLUE), (0, 100, "#2E7D32"), (100, 110, LIONS_BLUE)]   # end zone, field, end zone
    for start, end, color in pieces:
        start, end = max(start, first_yard), min(end, last_yard)
        if end > start:
            x, y = np.meshgrid([start, end], sides)
            ax.plot_surface(x, y, np.zeros_like(x), color=color, alpha=0.8, zorder=0)
    for yard in range(0, 101, 10):                 # yard lines
        if first_yard <= yard <= last_yard:
            ax.plot([yard, yard], sides, [0, 0], color="white", linewidth=1, zorder=1)
    ax.set_xlabel("Along field (yd)")
    ax.set_ylabel("Sideways (yd)")
    ax.set_zlabel("Height (ft)")


def plot_all_throws(df, view="normal", filename="output/3d_all_throws.png"):
    """Every throw that passed the checks, colored by complete or touchdown."""
    good = df[df["check"] == "OK"]
    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(projection="3d")
    draw_field(ax)
    for result, color in COLORS.items():
        for _, row in good[good["result"] == result].iterrows():
            along, sideways, height = ball_path(row)
            ax.plot(along, sideways, height, color=color, linewidth=2.5, zorder=3)
            ax.text(along[-1], sideways[-1], height[-1] + 2, f"#{row['number']}", fontsize=8)
        ax.plot([], [], color=color, linewidth=3, label=result)   # for the legend
    ax.set_xlim(-10, 110)
    ax.set_ylim(-27, 27)
    ax.set_zlim(0, 30)
    ax.set_box_aspect((120, 53.3, 25))
    ax.legend(loc="upper left")
    if view == "side":
        ax.view_init(elev=3, azim=-90)            # from the sideline, so you can see how high each throw went
        ax.set_yticks([])
        ax.set_ylabel("")
        ax.set_xlabel("Along field (yd)", labelpad=14)
        ax.set_title("All throws seen from the sideline")
    else:
        ax.view_init(elev=25, azim=-60)
        ax.set_title(f"All {len(good)} throws that passed the checks (gold = touchdown)")
    fig.savefig(filename, dpi=150, bbox_inches="tight")
    return fig


def plot_one_throw(df, number):
    """A close-up of one throw with its speed in the title."""
    row = df[df["number"] == number].iloc[0]
    along, sideways, height = ball_path(row)
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(projection="3d")
    first, last = min(along) - 5, max(along) + 5
    draw_field(ax, first, last)
    ax.plot(along, sideways, height, color=COLORS[row["result"]], linewidth=3, zorder=3)
    ax.scatter(along[0], sideways[0], height[0], color="black", s=40, zorder=4)
    ax.text(along[0], sideways[0], height[0] + 2, "throw", zorder=5)
    ax.scatter(along[-1], sideways[-1], height[-1], color="red", s=40, zorder=4)
    ax.text(along[-1], sideways[-1], height[-1] + 2, "catch", zorder=5)
    ax.set_xlim(first, last)
    ax.set_ylim(-27, 27)
    ax.set_zlim(0, max(height) + 8)
    ax.set_title(f"Throw #{number}: {row['distance_yd']} yd, {row['angle']:g} degrees, "
                 f"{row['speed_mph']} mph, {row['hang_time_s']} s in the air")
    ax.view_init(elev=20, azim=-70)
    fig.savefig(f"output/3d_throw_{number}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def animate_throw(df, number):
    """Make a GIF of the ball flying for one throw."""
    row = df[df["number"] == number].iloc[0]
    along, sideways, height = ball_path(row, points=60)
    fig = plt.figure(figsize=(9, 5.5))
    ax = fig.add_subplot(projection="3d")
    first, last = min(along) - 5, max(along) + 5
    draw_field(ax, first, last)
    ax.set_xlim(first, last)
    ax.set_ylim(-27, 27)
    ax.set_zlim(0, max(height) + 8)
    ax.view_init(elev=20, azim=-70)
    ax.set_title(f"Throw #{number}: {row['speed_mph']} mph")
    trail, = ax.plot([], [], [], color=COLORS[row["result"]], linewidth=3, zorder=3)
    ball, = ax.plot([], [], [], "o", color="saddlebrown", markersize=9, zorder=4)

    def update(i):
        trail.set_data_3d(along[:i + 1], sideways[:i + 1], height[:i + 1])
        ball.set_data_3d([along[i]], [sideways[i]], [height[i]])
        return trail, ball

    animation = FuncAnimation(fig, update, frames=len(along), interval=40)
    animation.save(f"output/animation_throw_{number}.gif", writer=PillowWriter(fps=25))
    plt.close(fig)
