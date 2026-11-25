"""
graphs.py

The four analysis graphs from my success criteria:
  1. angle histogram   2. speed histogram   3. distance vs angle   4. distance vs speed
Throws that failed the checks are shown in red so you can see them.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

LIONS_BLUE = "#0076B6"
RED = "#C8102E"


def angle_histogram(df):
    good = df[df["check"] == "OK"]["angle"]
    bad = df[df["check"] != "OK"]["angle"]
    plt.figure(figsize=(7, 4.5))
    plt.hist([good, bad], bins=range(-40, 55, 5), stacked=True, color=[LIONS_BLUE, RED],
             edgecolor="white", label=["passed checks", "flagged"])
    plt.axvline(0, color="black", linestyle="--", label="eye level (0 degrees)")
    plt.title("Angle above Goff's eye line")
    plt.xlabel("Angle (degrees)")
    plt.ylabel("Number of throws")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))   # whole numbers only
    plt.legend()
    plt.savefig("output/graph_angle_histogram.png", dpi=150, bbox_inches="tight")
    plt.close()


def speed_histogram(df):
    good = df[df["check"] == "OK"]["speed_mph"]
    plt.figure(figsize=(7, 4.5))
    plt.hist(good, bins=range(20, 80, 5), color=LIONS_BLUE, edgecolor="white")
    plt.axvline(good.mean(), color="black", label=f"average = {good.mean():.1f} mph")
    plt.title("Launch speed (throws that passed the checks)")
    plt.xlabel("Launch speed (mph)")
    plt.ylabel("Number of throws")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.legend()
    plt.savefig("output/graph_speed_histogram.png", dpi=150, bbox_inches="tight")
    plt.close()


def distance_vs_angle(df):
    good = df[df["check"] == "OK"]
    bad = df[df["check"] != "OK"]
    plt.figure(figsize=(7, 4.5))
    plt.scatter(good["distance_yd"], good["angle"], color=LIONS_BLUE, s=50, label="passed checks")
    plt.scatter(bad["distance_yd"], bad["angle"], color=RED, marker="x", s=50, label="flagged")
    plt.axhline(0, color="black", linestyle="--")
    plt.title("Throw distance vs angle")
    plt.xlabel("Ground distance (yd)")
    plt.ylabel("Angle above eye line (degrees)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig("output/graph_distance_vs_angle.png", dpi=150, bbox_inches="tight")
    plt.close()


def distance_vs_speed(df):
    good = df[df["check"] == "OK"]
    plt.figure(figsize=(7, 4.5))
    plt.scatter(good["distance_yd"], good["speed_mph"], color=LIONS_BLUE, s=50)
    for _, r in good.iterrows():
        plt.annotate(f"#{r['number']}", (r["distance_yd"], r["speed_mph"]), textcoords="offset points", xytext=(5, 5))
    plt.title("Throw distance vs launch speed")
    plt.xlabel("Ground distance (yd)")
    plt.ylabel("Launch speed (mph)")
    plt.grid(alpha=0.3)
    plt.savefig("output/graph_distance_vs_speed.png", dpi=150, bbox_inches="tight")
    plt.close()


def make_all_graphs(df):
    angle_histogram(df)
    speed_histogram(df)
    distance_vs_angle(df)
    distance_vs_speed(df)
