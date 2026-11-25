"""
check_formula.py  -  is my speed formula right?

I "throw" a ball at a speed I pick, work out where it comes down to catch height,
and then put that distance into my formula. If the formula is right, I get my speed back.
"""

import math

from throw_speed import CATCH_HEIGHT, EYE_HEIGHT, G, launch_speed, to_mph

for speed_mph, angle in [(40, 25), (50, 30), (60, 15)]:
    v = speed_mph * 5280 / 3600                    # mph -> ft/s
    a = math.radians(angle)
    # height = EYE_HEIGHT + v*sin(a)*t - 0.5*G*t^2 = CATCH_HEIGHT  -> solve the quadratic for t
    A, B, C = -0.5 * G, v * math.sin(a), EYE_HEIGHT - CATCH_HEIGHT
    t = (-B - math.sqrt(B * B - 4 * A * C)) / (2 * A)
    distance_ft = v * math.cos(a) * t
    answer = to_mph(launch_speed(distance_ft, angle, CATCH_HEIGHT - EYE_HEIGHT))
    print(f"threw at {speed_mph} mph and {angle} degrees -> landed {distance_ft / 3:.1f} yd away "
          f"-> formula says {answer:.2f} mph")
