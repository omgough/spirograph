# app.py — our web app
#
# Flask serves pages to the browser. NumPy does fast math.
# Matplotlib draws the spirograph into an image.

import io          # lets us hold an image in memory (no file needed)
import base64      # lets us turn an image into text to send to the browser
from math import gcd

import numpy as np

# Matplotlib normally expects a screen/window. On a web server there's
# no window, so we switch it to "Agg" — a mode that just draws to images.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ---- The spirograph math ----
# A spirograph curve is called a "hypotrochoid". It traces the path of a
# pen poked through a small circle that rolls around inside a big circle.
# It has three settings:
#   R = radius of the big (fixed) circle
#   r = radius of the small (rolling) circle  -> controls how many petals
#   d = how far the pen is from the small circle's center -> loop shape
def make_spirograph_image(x, y, rx, ry, color="#e0567a"):
    # The canvas in the browser is 400x400, with the circle centered at
    # (200, 200) and a radius of 180. We measure where the dot's center
    # is relative to that center.
    #   x, y   = where the dot is placed
    #   rx, ry = the dot's horizontal and vertical radius (its size + shape)
    cx, cy = 200, 200
    dx = x - cx
    dy = y - cy
    distance = (dx * dx + dy * dy) ** 0.5      # 0 (center) .. 180 (edge)
    frac = min(distance / 180.0, 1.0)          # same thing as 0.0 .. 1.0

    R = 180

    # KNOB 1 — petals: position from center sets the rolling circle size.
    # Closer to the edge -> smaller rolling circle -> MORE petals.
    r = int(round(90 - frac * 60))             # ranges from 90 down to 30
    if r < 1:
        r = 1

    # KNOB 2 — loopiness: the dot's overall SIZE sets the pen offset d.
    # Bigger dot -> bigger d -> loopier, more dramatic pattern.
    size = (rx + ry) / 2.0
    size = max(3.0, min(size, 150.0))          # keep it in a sane range
    d = 15 + (size / 150.0) * 115              # ranges from ~15 to ~130

    # KNOB 3 — stretch: the dot's SHAPE stretches the whole pattern.
    # A wide dot -> wide pattern; a tall dot -> tall pattern.
    rx = max(rx, 1.0)
    ry = max(ry, 1.0)
    aspect = rx / ry
    x_scale = aspect ** 0.5
    y_scale = 1.0 / x_scale

    # How many full turns until the pattern closes back on itself.
    turns = r // gcd(R, r)
    t = np.linspace(0, 2 * np.pi * turns, 4000)   # 4000 points along the path

    # The hypotrochoid formulas — this is the actual spirograph!
    xs = ((R - r) * np.cos(t) + d * np.cos((R - r) / r * t)) * x_scale
    ys = ((R - r) * np.sin(t) - d * np.sin((R - r) / r * t)) * y_scale

    # ---- Draw it with Matplotlib ----
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(xs, ys, color=color, linewidth=1.2)
    ax.set_aspect("equal")     # keep true proportions (no accidental squashing)
    ax.axis("off")             # hide the axes/numbers
    # Fit the view to the pattern with a little margin.
    m = max(np.abs(xs).max(), np.abs(ys).max()) * 1.05
    ax.set_xlim(-m, m)
    ax.set_ylim(-m, m)

    # Save the drawing into memory as a PNG (instead of a file on disk).
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)             # free the memory
    buffer.seek(0)

    # Turn the image bytes into a text string the browser can show.
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return "data:image/png;base64," + encoded


@app.route("/")
def home():
    return render_template("index.html")


# The browser sends a dot here; we send a spirograph picture back.
@app.route("/point", methods=["POST"])
def point():
    data = request.get_json()
    x = data["x"]
    y = data["y"]
    rx = data["rx"]            # dot's horizontal radius
    ry = data["ry"]            # dot's vertical radius
    color = data.get("color", "#e0567a")   # line colour (from the palette)
    print(f"Got a dot: x={x}, y={y}, rx={rx}, ry={ry}, color={color}")

    image = make_spirograph_image(x, y, rx, ry, color)   # do the math + draw it
    return jsonify({"image": image})              # send the picture back


if __name__ == "__main__":
    # Port 5000 is taken by macOS AirPlay, so we use 5001 instead.
    app.run(debug=True, port=5001)
