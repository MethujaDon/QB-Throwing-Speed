"""
main.py  -  run this file to do the whole project:   python main.py

1. read my Pass Log and work out the speed of every throw
2. save the results table
3. make the 4 analysis graphs
4. make the 3D pictures and the animated GIF
All the pictures go into the "output" folder.
"""

import os

import matplotlib.pyplot as plt

import field3d
import graphs
from throw_speed import analyze, load_throws, print_table

os.makedirs("output", exist_ok=True)

# Step 1: the math
df = analyze(load_throws("data/throws.xlsx"))
print_table(df)

# Step 2: save the results
df[["number", "Date", "Game", "Catcher", "result", "distance_yd", "angle", "speed_mph", "hang_time_s", "check"]] \
    .to_csv("output/results.csv", index=False)

# Step 3: graphs
graphs.make_all_graphs(df)

# Step 4: 3D pictures. I use the longest throw that passed the checks for the close-up and the GIF.
good = df[df["check"] == "OK"]
longest = int(good.loc[good["distance_yd"].idxmax(), "number"])
field3d.plot_all_throws(df, view="side", filename="output/3d_all_throws_side_view.png")
field3d.plot_one_throw(df, longest)
print("\nMaking the animated GIF (takes a few seconds)...")
field3d.animate_throw(df, longest)
field3d.plot_all_throws(df)          # this one stays open so you can rotate it with the mouse

print("Done! Everything is saved in the output folder.")
plt.show()
