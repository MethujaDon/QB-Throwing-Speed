"""
throw_speed.py

The math part of my project: how fast did Jared Goff throw the ball?

For each pass I have:
  - where Goff threw it from (sideways and along the field, in yards)
  - where it was caught (same thing)
  - the angle I estimated while watching the play: how many degrees ABOVE Goff's
    eye-level line (straight ahead and level with his eyes) the ball started out

From that I use projectile motion to work out the launch speed.
Run this file by itself to just print the results table:  python throw_speed.py
"""

import math

import numpy as np
import pandas as pd

# ---- numbers I assume ------------------------------------------------------
G = 32.174           # gravity, in feet per second squared
EYE_HEIGHT = 6.0     # Goff is 6'4", so his eyes are about 6 ft up. I measure the angle
                     # from his eye line, so I say the ball starts at this height.
CATCH_HEIGHT = 5.5   # I assume the ball is caught about chest high
MAX_SPEED_MPH = 70   # my limit for a realistic NFL throw; anything faster gets flagged

# Short names for the long column headers in my Pass Log
COLUMNS = {
    "Throwing position: sideways (yd from center)": "throw_x",
    "Throwing position: along field (yd from own goal line)": "throw_y",
    "Catching position: sideways (yd from center)": "catch_x",
    "Catching position: along field (yd from own goal line)": "catch_y",
    "Throw Angle": "angle",
}


def load_throws(path="data/throws.xlsx"):
    """Read my Pass Log. The column headers are on row 3 of the spreadsheet."""
    df = pd.read_excel(path, header=2)
    df = df.rename(columns=COLUMNS)
    df = df[df["throw_x"].notna()]                                   # skip empty rows
    df = df[~df["Game"].astype(str).str.contains("EXAMPLE")]         # skip the made-up example row
    # The Note column says "Result: Touchdown" or "Result: Complete"
    df["result"] = ["Touchdown" if "Touchdown" in str(note) else "Complete" for note in df["Note"]]
    df = df.reset_index(drop=True)
    df["number"] = df.index + 1                                      # throw #1, #2, ...
    return df


def ground_distance(x1, y1, x2, y2):
    """Distance along the ground in yards, using the Pythagorean theorem: d = sqrt(a^2 + b^2)."""
    sideways = x2 - x1
    along = y2 - y1
    return math.sqrt(sideways ** 2 + along ** 2)


def launch_speed(distance_ft, angle_deg, height_change_ft):
    """Launch speed in feet per second, or None if no speed could make this throw.

    From projectile motion (see README for all the steps):
        V = sqrt( g * d^2 / ( 2 * cos^2(angle) * (d * tan(angle) - dz) ) )
    d = ground distance (ft), dz = catch height - release height (ft).
    """
    if angle_deg <= -90 or angle_deg >= 90:
        return None
    angle = math.radians(angle_deg)
    bottom = 2 * math.cos(angle) ** 2 * (distance_ft * math.tan(angle) - height_change_ft)
    if bottom <= 0:
        # The ball would already be below the catch point before it got there,
        # even without gravity pulling it down. So this angle is impossible.
        return None
    return math.sqrt(G * distance_ft ** 2 / bottom)


def to_mph(feet_per_second):
    return feet_per_second * 3600 / 5280


def analyze(df):
    """Add distance, speed, hang time and a check result to every throw."""
    height_change = CATCH_HEIGHT - EYE_HEIGHT
    distances, speeds, hang_times, checks = [], [], [], []

    for _, row in df.iterrows():
        d_yd = ground_distance(row["throw_x"], row["throw_y"], row["catch_x"], row["catch_y"])
        d_ft = d_yd * 3
        v = launch_speed(d_ft, row["angle"], height_change)

        if v is None:
            speeds.append(None)
            hang_times.append(None)
            checks.append("impossible angle")
        else:
            mph = to_mph(v)
            speeds.append(round(mph, 1))
            hang_times.append(round(d_ft / (v * math.cos(math.radians(row["angle"]))), 2))
            checks.append("OK" if mph <= MAX_SPEED_MPH else "too fast to be real")
        distances.append(round(d_yd, 1))

    df["distance_yd"] = distances
    df["speed_mph"] = speeds
    df["hang_time_s"] = hang_times
    df["check"] = checks
    return df


def ball_path(row, points=100):
    """Points along the ball's flight for one throw (along field, sideways, height in ft)."""
    d_ft = row["distance_yd"] * 3
    v = row["speed_mph"] * 5280 / 3600                     # back to feet per second
    angle = math.radians(row["angle"])
    total_time = d_ft / (v * math.cos(angle))
    t = np.linspace(0, total_time, points)
    fraction = t / total_time                              # 0 at the throw, 1 at the catch
    along = row["throw_y"] + (row["catch_y"] - row["throw_y"]) * fraction
    sideways = row["throw_x"] + (row["catch_x"] - row["throw_x"]) * fraction
    height = EYE_HEIGHT + v * math.sin(angle) * t - 0.5 * G * t ** 2
    return along, sideways, height


def print_table(df):
    print(f"{'#':>3}  {'Game':28} {'Catcher':13} {'Dist (yd)':>9} {'Angle':>6} {'Speed (mph)':>12}  Check")
    for _, r in df.iterrows():
        speed = f"{r['speed_mph']:.1f}" if r["speed_mph"] is not None and r["speed_mph"] == r["speed_mph"] else "-"
        print(f"{r['number']:>3}  {r['Game']:28} {str(r['Catcher']):13} {r['distance_yd']:>9} {r['angle']:>6g} {speed:>12}  {r['check']}")
    good = df[df["check"] == "OK"]
    print(f"\n{len(good)} of {len(df)} throws passed the checks.")
    if len(good) > 0:
        print(f"Average launch speed of those throws: {good['speed_mph'].mean():.1f} mph")


if __name__ == "__main__":
    print_table(analyze(load_throws()))
